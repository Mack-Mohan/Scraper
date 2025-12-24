import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger("ScraperService")

class IScraperStrategy(ABC):
    """
    Interface for platform-specific scraping logic.
    """
    @property
    @abstractmethod
    def domain(self) -> str:
        """The domain this strategy supports (e.g., 'meesho.com')."""
        pass

    @abstractmethod
    def extract_cards(self, driver: WebDriver) -> List[WebElement]:
        """Locates product cards in the DOM."""
        pass

    @abstractmethod
    def parse_card(self, card: WebElement) -> Dict[str, Any]:
        """Extracts data from a single card."""
        pass

    @abstractmethod
    def load_more(self, driver: WebDriver) -> bool:
        """
        Loads the next batch of data. 
        Returns True if successful (new content loaded).
        Returns False if end of results.
        """
        pass