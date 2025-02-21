import time
from selenium.webdriver.common.by import By
from driver import setup_driver, safe_get
from bs4 import BeautifulSoup
import requests


def extract_categories(url, limit=None):
    """Scrape category names and URLs using BeautifulSoup (faster than Selenium)."""
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()  # Raise an error for failed requests

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all category elements
        categories = soup.find_all("div", class_="sidebar-item")
        
        if not categories:
            print("⚠️ No categories found. The page may require JavaScript rendering.")
            return {}

        cat_len = len(categories)
        local_limit = min(limit, cat_len) if limit else cat_len  # Ensure limit is within range
        extracted_categories = {}

        for category in categories[:local_limit]:
            try:
                category_anchor = category.find("a")  # Get <a> tag
                category_name = category_anchor.find("span").text.strip()  # Extract category name
                print(category_name)
                category_url = category_anchor["href"]  # Extract category URL
                print(category_url)
                
                # If URLs are relative, convert to absolute
                if category_url.startswith("/"):
                    category_url = f"https://www.tops.co.th{category_url}"

                subcategories = extract_subcategories(category_url, local_limit) if limit else extract_subcategories(category_url)

                extracted_categories[category_name] = subcategories

            except Exception as e:
                print("⚠️ Error extracting category:", e)

        print(f"✅ Extracted {len(extracted_categories)} categories successfully!")
        return extracted_categories

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return {}


from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def extract_subcategories(category_url, limit=None):
    """Extract subcategory names and URLs from a category page
    with optional limit. Uses BeautifulSoup after Selenium loads content."""
    
    driver = setup_driver()
    subcategories = []
    
    try:
        # Retry Logic
        if not safe_get(driver, category_url, "plp-carousel__link"):
            pass

        # Get page source after JavaScript execution
        soup = BeautifulSoup(driver.page_source, "lxml")
        
        # Extract subcategories using BeautifulSoup
        subcategory_links = soup.find_all("a", class_="plp-carousel__link")
        
        sub_len = len(subcategory_links)
        local_limit = min(limit, sub_len) if limit else sub_len  # Ensure limit is valid
        
        if subcategory_links:
            print(f"✅ Found {sub_len} subcategories in {category_url}")
            
            for link in subcategory_links[:local_limit] if limit else subcategory_links:
                try:
                    # subcategory_name = link.text.strip()
                    subcategory_url = link["href"]
                    subcategories.append(subcategory_url)
                except Exception as e:
                    print("⚠️ Error extracting subcategory:", e)
        else:
            print("⚠️ No subcategories found. JavaScript may not have fully executed.")
        
    except Exception as e:
        print(f"❌ Error loading category page: {e}")
    
    finally:
        driver.quit()
    
    return subcategories