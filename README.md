# Scraper Service

A modular Python scraping engine.

### 📂 Components
* **`main.py`**: The entry point. Initializes the driver, runs the engine, and saves data.
* **`strategies.py`**: Contains site-specific logic (CSS selectors, navigation) implementing the Strategy Pattern.
* **`scraper_config.py`**: Global settings (timeouts, headless mode, output filename).
* **`combined_products.xlsx`**: Pre-scraped dataset containing ~600 items per site for reference.

### ⚡ Installation
1.  **Install dependencies:**
    ```bash
    pip install selenium pandas openpyxl undetected-chromedriver
    ```
2.  **Requirements:** Google Chrome browser must be installed.

### 🚀 How to Run
1.  Open `main.py` and set your target links:
    ```python
    TARGET_URLS = [
        "[https://www.meesho.com/search?q=saree](https://www.meesho.com/search?q=saree)",
        "[https://www.myntra.com/men-tshirts](https://www.myntra.com/men-tshirts)"
    ]
    ```
2.  **Execute the script:**
    ```bash
    python main.py
    ```

### 🎯 What it Does
1.  **Detects Platform:** Automatically selects the correct strategy (Meesho vs. Myntra) based on the URL.
2.  **Navigates:** Handles infinite scrolling (Meesho) or clicks "Next" buttons (Myntra).
3.  **Extracts:** Scrapes Title, Price, Image URL, and Product Link.
4.  **Saves:** Aggregates data from all sites into `combined_products.xlsx` (appending to or overwriting the existing sample file).
