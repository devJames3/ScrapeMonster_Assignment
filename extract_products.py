from utils import scroll_to_load_all_products, extract_paragraphs_with_newlines, extract_quantity, is_valid_ean_upc
from concurrent.futures import ThreadPoolExecutor, as_completed
from driver import setup_driver, safe_get
from utils import save_json_in_batches
from bs4 import BeautifulSoup

def fetch_product_links(subcategory_url, limit=None):
    """Extract product links from a single 'View All' subcategory page."""
    driver = setup_driver()
    product_links = []

    try:
        # Retry Logic
        if not safe_get(driver, subcategory_url, "product-item-inner-wrap"):
            return []

        scroll_to_load_all_products(driver)

        soup = BeautifulSoup(driver.page_source, "lxml")

        # Find all product cards
        product_elements = soup.find_all("a", class_="product-item-inner-wrap") 
        product_len = len(product_elements)
        local_limit = min(limit, product_len) if limit else product_len  # Ensure limit is not exceeded

        if product_elements:
            print(f"✅ Found {product_len} products in {subcategory_url}")
            for product in product_elements[:local_limit] if limit else product_elements:
                try:
                    product_url = product["href"]
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


def extract_product_links(subcategories, max_workers, limit=None):
    """Extract product links from multiple 'View All' subcategory pages concurrently."""
    products = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_category = {}

        for category, subcategory_list in subcategories.items():
            products[category] = []
            for subcategory_url in subcategory_list:
                future = executor.submit(fetch_product_links, subcategory_url, limit)
                future_to_category[future] = category

        for future in as_completed(future_to_category):
            category = future_to_category[future]
            try:
                products[category].extend(future.result())  # Collect product links
            except Exception as e:
                print(f"❌ Error processing category {category}: {e}")

    return products


def fetch_product_details(category, product_url):
    """Fetch and extract product details from a single page using its own WebDriver."""
    driver = setup_driver()
    try:
        if not safe_get(driver, product_url, "product-Details-page-root"):
            return None
        
        product_details = {}
        soup = BeautifulSoup(driver.page_source, "lxml")
        product_container = soup.find("div", class_="product-Details-page-root")

        if product_container:
            product_name = product_container.get("data-product-name", "N/A")
            product_sku = product_container.get("data-product-id", "N/A")

            # Extract properties
            property_container = product_container.find("div", class_="accordion-property")
            properties_text = extract_paragraphs_with_newlines(property_container) if property_container else "N/A"

            ingredient_container = product_container.find("div", class_="accordion-ingredient")
            ingredient_text = extract_paragraphs_with_newlines(ingredient_container) if ingredient_container else "N/A"

            usage_container = product_container.find("div", class_="accordion-direction")
            usage_text = extract_paragraphs_with_newlines(usage_container) if usage_container else "N/A"

            description_link = "N/A"
            description_container_image = product_container.find("div", class_="accordion-item-description")
            if description_container_image:
                p = description_container_image.find("p")
                if p:
                    img = p.find("img")
                    if img and "src" in img.attrs:
                        description_link = img["src"]

            description_container_video = product_container.find("div", class_="youtube-embed-wrapper")
            if description_container_video:
                iframe = description_container_video.find("iframe")
                if iframe and "src" in iframe.attrs:
                    description_link = f'https:{iframe["src"]}'

            product_description = f"Properties:\n{properties_text}\n\nIngredients:\n{ingredient_text}\n\nUsage:\n{usage_text}\n\nDescription:\n{description_link}"

            product_details["productName"] = product_name
            img_container = product_container.find("div", class_="product-Details-images")
            img_tags = img_container.find_all("img") if img_container else []
            product_details["productImages"] = list(set(img["src"] for img in img_tags if "src" in img.attrs))

            product_details["quantity"] = extract_quantity(product_name)
            product_details["barCodeNumber"] = product_sku if product_sku and is_valid_ean_upc(product_sku) else "N/A"
            product_details["productDetails"] = product_description 

            product_price = product_container.get("data-product-price-new")
            product_details["price"] = {
                "value": float(product_price) if product_price else None,
                "currency": "THB",
            }

            product_details["label"] = product_container.get("data-product-badge-label", "N/A")
            
            return category, product_details
        else:
            print(f"⚠️ Product details not found for {product_url}")

    except Exception as e:
        print(f"❌ Error extracting product details from {product_url}: {e}")

    finally:
        driver.quit()

    return None



def extract_product_details(products, max_workers, batch_size=50):
    """Extract detailed product information and save in batches."""
    product_data = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for category, product_list in products.items():
            for product_url in product_list:
                futures.append(executor.submit(fetch_product_details, category, product_url))

        batch = {}
        for future in as_completed(futures):
            result = future.result()
            if result:
                category, details = result
                if category not in batch:
                    batch[category] = []
                batch[category].append(details)

                # Save batch every `batch_size` products
                if sum(len(v) for v in batch.values()) >= batch_size:
                    save_json_in_batches(batch, batch_size)
                    batch = {}

        # save remaining products
        if batch:
            save_json_in_batches(batch, batch_size)

    return product_data
