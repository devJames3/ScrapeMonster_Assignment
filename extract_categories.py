import time
from selenium.webdriver.common.by import By
from driver import setup_driver, safe_get


def extract_categories(url, limit=None):
    """Scrape category names and URLs from the Tops Online website. 
    with optional limit"""

    driver = setup_driver()
    
    try: 
        if not safe_get(driver, url, "sidebar-item"):
            return {}
        # driver.get(url)
        # time.sleep(5)  # Allow JavaScript to render content
        
        # Find categories
        categories = driver.find_elements(By.CLASS_NAME, "sidebar-item")
        cat_len = len(categories)
        local_limit = min(limit, cat_len) if limit else cat_len # Ensure limit is not more than the categories
        if categories:
            print(f"✅ Homepage loaded successfully! Found {cat_len} categories.")
            extracted_categories = {}

            for category in categories[:local_limit] if limit else categories:
                try:
                    category_anchor = category.find_element(By.TAG_NAME, "a")  # Get <a> tag
                    category_span = category_anchor.find_element(By.TAG_NAME, "span")  # Get <span> inside <a>
                    category_name = category_span.get_attribute("innerText").strip()  # Extract text
                    category_url = category_anchor.get_attribute("href")  # Extract link
                    subcategories = extract_subcategories(category_url, local_limit) if limit else extract_subcategories(category_url)

                    extracted_categories[category_name] = subcategories

                except Exception as e:
                    print("⚠️ Error extracting category:", e)
            
            return extracted_categories 
        else:
            print("⚠️ Homepage loaded but no categories found. JavaScript may not have fully executed.")
            return {}

    except Exception as e:
        print(f"❌ Error loading homepage: {e}")
        return {}
    
    finally:
        driver.quit()


def extract_subcategories(category_url, limit=None):
    """Extract subcategory names and URLs from a category page
    with optional limit"""

    driver = setup_driver()
    subcategories = []
    
    try:
        if not safe_get(driver, category_url, "plp-carousel__link"):
            return []
        # driver.get(category_url)
        # time.sleep(5)  # Allow JavaScript to render content
        
        # Find "View All" links in subcategories
        subcategory_links = driver.find_elements(By.CLASS_NAME, "plp-carousel__link")
        sub_len = len(subcategory_links)
        local_limit = min(limit, sub_len) if limit else sub_len # Ensure limit is not more than the sub-categories
        if subcategory_links:
            print(f"✅ Found {sub_len} subcategories in {category_url}")
            for link in subcategory_links[:local_limit] if limit else subcategory_links:
                try:
                    # subcategory_name = link.text.strip()
                    subcategory_url = link.get_attribute("href")
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