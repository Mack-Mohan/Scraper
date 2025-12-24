import logging
import time
from typing import List
from platform_strategies.abstract import IScraperStrategy
from typing import List, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

logger = logging.getLogger("ScraperService")

class MyntraStrategy(IScraperStrategy):
    @property
    def domain(self) -> str:
        return "myntra.com"

    def extract_cards(self, driver: WebDriver) -> List[WebElement]:
        return driver.find_elements(By.XPATH, "//li[contains(@class, 'product-base')]")

    def parse_card(self, card: WebElement) -> Dict[str, Any]:
        data = {
            "title": None,
            "price": None, 
            "image_url": None, 
            "product_url": None,
            "plaftorm": "Myntra"
        }
        
        try:
            # 1. IMAGE
            try: 
                img_el = card.find_element(By.TAG_NAME, "img")
                data["image_url"] = img_el.get_attribute("src")
            except: 
                pass

            # CRITICAL: If no image, return empty dict immediately to skip this item
            if not data["image_url"]:
                return {} 

            # 2. Title
            try:
                brand = card.find_element(By.XPATH, ".//h3[contains(@class, 'product-brand')]").text
                name = card.find_element(By.XPATH, ".//h4[contains(@class, 'product-product')]").text
                data["title"] = f"{brand} - {name}"
            except: 
                data["title"] = card.text.split('\n')[0]

            # 3. Price
            try:
                data["price"] = card.find_element(By.XPATH, ".//span[contains(@class, 'product-discountedPrice')]").text.replace('Rs.','').strip()
            except:
                try: 
                    raw = card.find_element(By.XPATH, ".//div[contains(@class, 'product-price')]").text
                    if "Rs." in raw: data["price"] = raw.replace('Rs.','').split()[0].strip()
                except: pass

            # 4. Link
            try: data["product_url"] = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            except: pass
            
        except: 
            return {}
            
        return data
    def load_more(self, driver: WebDriver) -> bool:
        """Implementation: CLICK THE 'LI' NEXT ELEMENT"""
        logger.info("Looking for 'Next' button...")
        
        try:
            next_btn = driver.find_element(By.XPATH, "//li[contains(@class, 'pagination-next')]")
            
            if "pagination-disabled" in next_btn.get_attribute("class"):
                logger.info("Next button is disabled. End of pages.")
                return False

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(1) 
            
            # Force Click using JavaScript 
            driver.execute_script("arguments[0].click();", next_btn)
            
            logger.info("Clicked Next button successfully.")
            time.sleep(5) # Wait for new page to load
            return True

        except Exception as e:
            logger.warning(f"Could not click Next button: {e}")
            return False