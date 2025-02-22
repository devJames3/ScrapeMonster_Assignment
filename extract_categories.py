import requests
from bs4 import BeautifulSoup
from driver import setup_driver, safe_get
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_categories(url, max_workers, limit=None):
    """Scrape category names and URLs using BeautifulSoup (faster than Selenium)."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        categories = soup.find_all("div", class_="sidebar-item")
        
        if not categories:
            print(f"⚠️ No categories found on {url}. The page may need JavaScript execution.")
            return {}

        cat_len = len(categories)
        local_limit = min(limit, cat_len) if limit else cat_len
        extracted_categories = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_category = {}

            for category in categories[:local_limit]:
                try:
                    category_anchor = category.find("a")
                    category_name = category_anchor.find("span").text.strip()
                    category_url = category_anchor["href"]

                    if category_url.startswith("/"):
                        category_url = f"https://www.tops.co.th{category_url}"

                    # Fetch subcategories concurrently
                    future = executor.submit(extract_subcategories, category_url, max_workers, local_limit)
                    future_to_category[future] = category_name

                except Exception as e:
                    print(f"⚠️ Error extracting category: {e}")

            # Collect results as they complete
            for future in as_completed(future_to_category):
                category_name = future_to_category[future]
                try:
                    extracted_categories[category_name] = future.result()
                except Exception as e:
                    print(f"❌ Error processing category '{category_name}': {e}")

        print(f"✅ Extracted {len(extracted_categories)} categories successfully!")
        return extracted_categories

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return {}


def extract_subcategories(category_url, max_workers, limit=None):
    """Extract subcategory names & URLs from a category page using concurrency."""
    driver = setup_driver()
    
    try:
        if not safe_get(driver, category_url, "plp-carousel__link"):
            print(f"⚠️ Failed to load subcategory page: {category_url}")
            return []

        soup = BeautifulSoup(driver.page_source, "lxml")
        subcategory_links = soup.find_all("a", class_="plp-carousel__link")
        sub_len = len(subcategory_links)
        local_limit = min(limit, sub_len) if limit else sub_len

        if not subcategory_links:
            print(f"⚠️ No subcategories found in {category_url}")
            return []

        print(f"✅ Found {sub_len} subcategories in {category_url}")

        # Extract URLs concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(lambda link: link["href"], link): link for link in subcategory_links[:local_limit]}
            return [future.result() for future in as_completed(futures)]

    except Exception as e:
        print(f"❌ Error loading category page: {e}")
        return []

    finally:
        driver.quit()
