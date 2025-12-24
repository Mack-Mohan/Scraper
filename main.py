import sys
import time
import logging
import pandas as pd
import undetected_chromedriver as uc
from typing import List
from urllib.parse import urlparse

from platform_strategies.abstract import IScraperStrategy
from platform_strategies.meesho import MeeshoStrategy
from platform_strategies.myntra import MyntraStrategy
from scraper_config import ScraperConfig


# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(module)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ScraperService")

# --- DRIVER FACTORY ---
class WebDriverFactory:
    @staticmethod
    def create_driver() -> uc.Chrome:
        logger.info("Initializing Browser...")
        options = uc.ChromeOptions()
        options.add_argument(ScraperConfig.WINDOW_SIZE)
        options.add_argument(ScraperConfig.DISABLE_POPUP)
        
        if ScraperConfig.HEADLESS:
             options.add_argument("--window-position=-10000,0")

        return uc.Chrome(options=options)

# --- ENGINE ---
class ScraperEngine:
    def __init__(self, strategies: List[IScraperStrategy]):
        self.strategies = {s.domain: s for s in strategies}
        self.driver = None

    def _get_strategy(self, url: str) -> IScraperStrategy:
        domain = urlparse(url).netloc
        for key, strategy in self.strategies.items():
            if key in domain:
                return strategy
        raise ValueError(f"No strategy found for domain: {domain}")

    def run(self, url: str, max_items: int) -> pd.DataFrame:
        strategy = self._get_strategy(url)
        logger.info(f"--- Starting Scrape for: {strategy.domain} ---")
        
        self.driver = WebDriverFactory.create_driver()
        all_data = []

        try:
            self.driver.get(url)
            time.sleep(5) 

            while len(all_data) < max_items:
                # 1. EXTRACT visible cards
                cards = strategy.extract_cards(self.driver)
                logger.info(f"Page loaded. Found {len(cards)} items.")
                
                # 2. PARSE
                for card in cards:
                    if len(all_data) >= max_items: 
                        break # Stop if we have enough
                        
                    item = strategy.parse_card(card)
                    item['source'] = strategy.domain
                    
                    # Avoid duplicates (Simple check based on Product URL)
                    if item.get('product_url') and not any(d.get('product_url') == item['product_url'] for d in all_data):
                        if item.get('title') or item.get('price'):
                            all_data.append(item)

                if len(all_data) >= max_items:
                    break

                # 3. NAVIGATION (The Generic Call!)
                logger.info(f"Collected {len(all_data)} items. Attempting to load more...")
                success = strategy.load_more(self.driver)
                
                if not success:
                    logger.info("No more content available.")
                    break

        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        
        return pd.DataFrame(all_data)

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. DEFINE YOUR TARGETS HERE
    TARGET_URLS = [
        "https://www.meesho.com/search?q=saree",
        "https://www.myntra.com/men-tshirts"
    ]
    MAX_ITEMS_PER_SITE = 600

    # 2. Register Strategies
    strategies = [
        MeeshoStrategy(),
        MyntraStrategy()
    ]
    
    engine = ScraperEngine(strategies)
    final_results = []

    # 3. Loop through URLs
    for url in TARGET_URLS:
        try:
            df = engine.run(url, MAX_ITEMS_PER_SITE)
            if not df.empty:
                final_results.append(df)
        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")

    # 4. Combine and Save
    if final_results:
        # Stack both dataframes on top of each other
        master_df = pd.concat(final_results, ignore_index=True)
        
        filename = "combined_products.xlsx"
        master_df.to_excel(filename, index=False)
        
        logger.info(f"\nSUCCESS! Combined {len(master_df)} items from {len(TARGET_URLS)} sites.")
        logger.info(f"Saved to: {filename}")
        print(master_df.head())
    else:
        logger.warning("No data found for any site.")