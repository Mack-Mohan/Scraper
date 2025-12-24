import logging
import time
from typing import List
from platform_strategies.abstract import IScraperStrategy
from typing import List, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

logger = logging.getLogger("ScraperService")

class MeeshoStrategy(IScraperStrategy):
    @property
    def domain(self) -> str:
        return "meesho.com"

    def extract_cards(self, driver: WebDriver) -> List[WebElement]:
        # Using partial match for robustness
        xpath = "//div[contains(@class, 'NewProductCardstyled__CardStyled')]"
        return driver.find_elements(By.XPATH, xpath)

    def parse_card(self, card: WebElement) -> Dict[str, Any]:
        data = {
            "title": None,
            "price": None,
            "image_url": None,
            "product_url": None,
            "platform": "Meesho"
        }
        
        try:
            # 1. Title
            try:
                title_el = card.find_element(By.XPATH, ".//p[contains(@class, 'ProductTitle')]")
                data["title"] = title_el.text.strip()
            except:
                pass 

            # 2. Price
            try:
                price_el = card.find_element(By.XPATH, ".//div[contains(@class, 'PriceRow')]//h5")
                data["price"] = price_el.text.replace('₹', '').strip()
            except:
                pass

            # 3. Image
            try:
                img_el = card.find_element(By.XPATH, ".//img")
                data["image_url"] = img_el.get_attribute("src")
            except:
                pass

            # 4. Link 
            try:
                link_el = card.find_element(By.XPATH, "./ancestor::a")
                data["product_url"] = link_el.get_attribute("href")
            except:
                pass

        except Exception as e:
            logger.warning(f"Error parsing card: {e}")
            
        return data
    
    def load_more(self, driver: WebDriver) -> bool:
        """Implementation: SCROLL DOWN"""
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Wait for load
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # If height increased, return true
        return new_height > last_height
