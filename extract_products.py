import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from driver import setup_driver
from utils import scroll_to_load_all_products, extract_paragraphs_with_newlines, extract_quantity, is_valid_ean_upc

def extract_product_links(subcategories, limit=None):
    """Extract product links from a 'View All' page."""
    driver = setup_driver()
    products = {}
    
    try:
        for category, subcategory_list in subcategories.items():
            for subcategory_url in subcategory_list:
                try:
                    driver.get(subcategory_url)
                    time.sleep(5)  # Allow JavaScript to render content
                    product_links = []
            
                    # Scroll until all products are loaded
                    scroll_to_load_all_products(driver)
            
                    # Find all product cards
                    product_elements = driver.find_elements(By.CLASS_NAME, "product-item-inner-wrap") 
                    product_len = len(product_elements)
                    local_limit = min(limit, product_len) if limit else product_len # Ensure limit is not more than the products
                    if product_elements:
                        print(f"✅ Found {product_len} products in {subcategory_url}")
                        for product in product_elements[:local_limit] if limit else product_elements:
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
            products[category] = product_links

    except Exception as e:
        print(f"❌ An Error Occurred: {e}")
    finally:
        driver.quit()
            

    return products


def extract_product_details(products):
    """Extract detailed product information from its page."""
    driver = setup_driver()
    product_data = {}

    try:
        for category, product_list in products.items():
            product_data[category] = []

            for product_url in product_list:
               
                try:
                    driver.get(product_url)
                    time.sleep(5)  # Allow JavaScript to render content
                    product_details = {}
                    
                    # Use BeautifulSoup to parse the page source
                    soup = BeautifulSoup(driver.page_source, "lxml")

                    # Find product details container
                    product_container = soup.find("div", class_="product-Details-page-root")
                    
                    if product_container:
                        product_name = product_container.get("data-product-name", "N/A")
                        product_sku = product_container.get("data-product-id", "N/A")

                        property_container = product_container.find("div", class_="accordion-property")
                        properties_text = extract_paragraphs_with_newlines(property_container) if property_container else "N/A"

                        ingredient_container = product_container.find("div", class_="accordion-ingredient")
                        ingredient_text = extract_paragraphs_with_newlines(ingredient_container) if ingredient_container else "N/A"

                        usage_container = product_container.find("div", class_="accordion-direction")
                        usage_text = extract_paragraphs_with_newlines(usage_container) if usage_container else "N/A"

                        description_link = "N/A"

                        # Check if description image container exists
                        description_container_image = product_container.find("div", class_="accordion-item-description")
                        if description_container_image:
                            p = description_container_image.find("p")
                            if p:
                                img = p.find("img")
                                if img and "src" in img.attrs:
                                    description_link = img["src"]

                        # Check if video container exists
                        description_container_video = product_container.find("div", class_="youtube-embed-wrapper")
                        if description_container_video:
                            iframe = description_container_video.find("iframe")
                            if iframe and "src" in iframe.attrs:
                                description_link = f'https:{iframe["src"]}'

                        product_description = f"Properties:\n{properties_text}\n\nIngredients:\n{ingredient_text}\n\nUsage:\n{usage_text}\n\nDescription:\n{description_link}"

                        product_details["productName"] = product_name

                        # Extract all images
                        img_container = product_container.find("div", class_="product-Details-images")
                        img_tags = img_container.find_all("img")
                        product_details["productImages"] = list(set([img["src"] for img in img_tags if "src" in img.attrs] if img_tags else []))

                        product_details["quantity"] = extract_quantity(product_name)

                        product_details["barCodeNumber"] = product_sku if is_valid_ean_upc(product_sku) else "N/A"

                        product_details["productDetails"] = product_description 

                        product_details["price"] = {
                            "value": product_container.get("data-product-price-new", "N/A"),
                            "currency": "THB" #Assuming it is a Thailand retailer
                        }

                        product_details["label"] = product_container.get("data-product-badge-label", "N/A")
                        
                        product_data[category].append(product_details) 
                    
                    else:
                        print("⚠️ Product details not found!")

                except Exception as e:
                    print(f"❌ Error extracting product details: {e}")

    except Exception as e:
        print(f"❌ An Error Occurred: {e}")
    finally:
        driver.quit()

    return product_data
