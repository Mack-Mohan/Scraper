class ScraperConfig:
    """Central configuration for the scraping service."""
    DEFAULT_TIMEOUT = 10
    SCROLL_PAUSE_TIME = 3
    OUTPUT_FILE = "scraped_data.xlsx"
    MAX_RETRIES = 3
    
    # Browser Settings
    HEADLESS = False
    WINDOW_SIZE = "--start-maximized"
    DISABLE_POPUP = "--disable-popup-blocking"