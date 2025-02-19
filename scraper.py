from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re


def setup_driver():
    """Initialize and return a Selenium WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_categories():
    """Scrape category names and URLs from the Tops Online website."""
    url = "https://www.tops.co.th/en"
    driver = setup_driver()
    
    try:
        driver.get(url)
        time.sleep(5)  # Allow JavaScript to render content

        # Find categories
        categories = driver.find_elements(By.CLASS_NAME, "sidebar-item")

        if categories:
            print(f"✅ Homepage loaded successfully! Found {len(categories)} categories.")
            extracted_categories = {}

            for category in categories:
                try:
                    category_anchor = category.find_element(By.TAG_NAME, "a")  # Get <a> tag
                    category_span = category_anchor.find_element(By.TAG_NAME, "span")  # Get <span> inside <a>
                    category_name = category_span.get_attribute("innerText").strip()  # Extract text
                    category_url = category_anchor.get_attribute("href")  # Extract link
                    subcategories = extract_subcategories(category_url)

                    extracted_categories[category_name] = subcategories
                    # {.append(}{"name": category_name, "subcategories": category_url})



                except Exception as e:
                    print("⚠️ Error extracting category:", e)
            
            return extracted_categories
        else:
            print("⚠️ Homepage loaded but no categories found. JavaScript may not have fully executed.")
            return []

    except Exception as e:
        print(f"❌ Error loading homepage: {e}")
        return []
    
    finally:
        driver.quit()


def extract_subcategories(category_url):
    """Extract subcategory names and URLs from a category page."""
    driver = setup_driver()
    subcategories = []
    
    try:
        driver.get(category_url)
        time.sleep(5)  # Allow JavaScript to render content
        
        # Find "View All" links in subcategories
        subcategory_links = driver.find_elements(By.XPATH, "//a[@data-testid='lnk-viewProductListing-viewAllItems']")
        
        if subcategory_links:
            print(f"✅ Found {len(subcategory_links)} subcategories in {category_url}")
            for link in subcategory_links:
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


def scroll_to_load_all_products(driver):
    """Scroll down repeatedly to ensure all products are loaded."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time for new products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Stop when no new content loads
        last_height = new_height

def extract_product_links(subcategory_url):
    """Extract product links from a 'View All' page."""
    driver = setup_driver()
    product_links = []
    
    try:
        driver.get(subcategory_url)
        time.sleep(5)  # Allow JavaScript to render content
        
        # Scroll until all products are loaded
        scroll_to_load_all_products(driver)
        
        # Find all product cards
        product_elements = driver.find_elements(By.CLASS_NAME, "product-item-inner-wrap")
        
        if product_elements:
            print(f"✅ Found {len(product_elements)} products in {subcategory_url}")
            for product in product_elements:
                try:
                    # product_anchor = product.find_element(By.TAG_NAME, "a")
                    product_url = product.get_attribute("href")
                    product_links.append(product_url)
                except Exception as e:
                    print("⚠️ Error extracting product link:", e)
        else:
            print("⚠️ No products found on the page. JavaScript may not have fully executed.")
        
    except Exception as e:
        print(f"❌ Error loading subcategory page: {e}")
    
    finally:
        driver.quit()
    
    return product_links


def extract_quantity(product_name):
    """
    Extracts the quantity from a product name.
    Supports kg, g, L, ml, with or without spaces.
    """
    # Updated regex to allow optional space between number and unit
    quantity_pattern = r"(\d+\.?\d*)\s*(kg|g|ltr|ml|Kg|G|Ltr|Ml|KG|LTR|ML)?"

    # Search for quantity in the product name
    match = re.search(quantity_pattern, product_name, re.IGNORECASE)

    if match and match.group(2):  # Ensure a unit was found
        return f"{match.group(1)}{match.group(2).lower()}"  # Standardize unit to lowercase
    
    return "N/A"  # Return "N/A" if no quantity is found

def is_valid_ean_upc(sku):
    """Validate if the SKU is a proper EAN/UPC barcode."""
    if not sku.isdigit():
        return False  # Must be numeric

    length = len(sku)
    if length not in [8, 12, 13, 14]:
        return False  # Must be EAN-8, UPC-12, EAN-13, or EAN-14

    return validate_ean_upc_checksum(sku)  # Checksum validation


def validate_ean_upc_checksum(barcode):
    """Validate EAN/UPC checksum using the official algorithm."""
    digits = [int(d) for d in barcode]
    length = len(digits)

    # Compute the checksum
    if length in [8, 12, 13, 14]:
        check_digit = digits[-1]  # Last digit is the check digit
        odd_sum = sum(digits[-2::-2])  # Sum of digits at odd positions (from right, excluding last)
        even_sum = sum(digits[-3::-2])  # Sum of digits at even positions (from right)

        if length in [8, 12, 14]:  # UPC, EAN-8, or EAN-14
            total = (odd_sum * 3) + even_sum
        else:  # EAN-13
            total = (even_sum * 3) + odd_sum

        calculated_check_digit = (10 - (total % 10)) % 10

        return check_digit == calculated_check_digit  # Must match the last digit

    return False  # Invalid length



def extract_product_details(product_url):
    """Extract detailed product information from its page."""
    driver = setup_driver()
    product_data = {}

    try:
        driver.get(product_url)
        time.sleep(5)  # Allow JavaScript to render content
        
        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(driver.page_source, "lxml")

        # Find product details container
        product_container = soup.find("div", class_="product-Details-page-root")
        
        if product_container:
            product_name = product_container.get("data-product-name", "N/A")
            product_data["productName"] = product_name

            # Extract all images
            img_container = product_container.find("div", class_="product-Details-images")
            img_tags = img_container.find_all("img")
            product_data["productImages"] = list(set([img["src"] for img in img_tags if "src" in img.attrs] if img_tags else []))

            product_data["quantity"] = extract_quantity(product_name)

            product_data["price"] = product_container.get("data-product-price-new", "N/A")
            product_data["sku"] = product_container.get("data-product-id", "N/A")
            

            # Extract promotions (if available)
            promotion = product_container.find("div", class_="promotion-text")
            product_data["promotion"] = promotion.text.strip() if promotion else "None"
        
        else:
            print("⚠️ Product details not found!")

    except Exception as e:
        print(f"❌ Error extracting product details: {e}")

    finally:
        driver.quit()

    return product_data

# if __name__ == "__main__":
#     categories = extract_categories()
#     print("\n✅ Final List of Categories with URLs:", categories)

# if __name__ == "__main__":
#     test_category_url = "https://www.tops.co.th/en/fruit-and-vegetables"  # Replace with actual category URL
#     subcategories = extract_subcategories(test_category_url)
#     print("\n✅ Final List of Subcategories with URLs:", subcategories)

# if __name__ == "__main__":
#     test_subcategory_url = "https://www.tops.co.th/en/fruit-and-vegetables/grapes-cherries-berries"  # Replace with an actual subcategory URL
#     product_links = extract_product_links(test_subcategory_url)
#     print("\n✅ Final List of Product URLs:", product_links)

if __name__ == "__main__":
    print(is_valid_ean_upc("0218720000006"))
    # test_subcategory_url = "https://www.tops.co.th/en/fruit-and-vegetables/grapes-cherries-berries"
    
    # # Step 1: Extract product links from subcategory
    # product_links = extract_product_links(test_subcategory_url)
    
    # # Step 2: Extract full details from each product page
    # all_product_data = []
    # for link in product_links[:5]:  # Limit to first 5 products for testing
    #     product_details = extract_product_details(link)
    #     all_product_data.append(product_details)

    # print("\n✅ Extracted Product Details:", all_product_data)