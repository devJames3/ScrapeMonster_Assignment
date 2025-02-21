import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

def setup_driver():
    """Initialize and return a Selenium WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    return driver


def safe_get(driver, url, classname=None, max_retries=3, timeout=30):
    """Attempts to load a URL with retries and explicit waiting."""
    for attempt in range(max_retries):
        try:
            driver.get(url)  # Load the page
            if classname:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, classname))
                )
            # print(f"✅ Successfully loaded: {url}")
            return True  # Page loaded successfully
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {url}")
            time.sleep(5)  # Wait before retrying
    
    print(f"❌ Failed to load after {max_retries} attempts: {url}")
    return False  # Page failed to load
