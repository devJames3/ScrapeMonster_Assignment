import re
import time
import logging
import json
from stdnum import ean
import os



def scroll_to_load_all_products(driver):
    """Scroll down repeatedly to ensure all products are loaded."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) 
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Stop when no new content loads
        last_height = new_height

def extract_quantity(product_name):
    """
    Extracts the quantity from a product name.
    Supports kg, g, L, ml, with or without spaces.
    """
    # regex allow optional space between number and unit
    quantity_pattern = r"(\d+\.?\d*)\s*(kg|g|ltr|ml|Kg|G|Ltr|Ml|KG|LTR|ML)?"

    match = re.search(quantity_pattern, product_name, re.IGNORECASE)

    if match and match.group(2):
        return f"{match.group(1)}{match.group(2).lower()}"
    
    return "N/A"

def is_valid_ean_upc(sku):
    """Validate if the SKU is a proper EAN/UPC barcode."""
    sku = sku.strip()
    if not sku.isdigit():
        return False
    
    return ean.is_valid(sku)

def extract_paragraphs_with_newlines(div):
    """Extract all <p> tags from a div, preserving <br> tags as new lines."""
    paragraphs = div.find_all("p")
    
    extracted_text = []
    for p in paragraphs:
        text = p.get_text(separator="\n", strip=True)  # <br> becomes \n
        extracted_text.append(text)
    
    return "\n".join(extracted_text)

def remove_duplicates(data):
    """Deduplicate products (based on name + SKU)"""
    
    for category, products in data.items():
        seen = set()
        unique_products = []
        
        for product in products:
            identifier = (product['productName'], product['barCodeNumber'])
            if identifier not in seen:
                seen.add(identifier)
                unique_products.append(product)
        
        data[category] = unique_products
    return data


def save_json_in_batches(data, batch_size=50, output_file="products.json"):
    """Save product data in batches while ensuring deduplication based on (productName + SKU)."""
    
    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # Ensure `existing_data` follows the same category structure
    for category, products in data.items():
        if category not in existing_data:
            existing_data[category] = []
        
        existing_keys = {f"{p['productName'].strip()}_{p.get('barCodeNumber', 'N/A').strip()}" for p in existing_data[category]}

        batch = []
        for product in products:
            product_name = product.get("productName", "").strip()
            sku = product.get("barCodeNumber", "N/A").strip()
            unique_key = f"{product_name}_{sku}"

            # Only add if the (productName + SKU) combination is unique
            if unique_key not in existing_keys:
                batch.append(product)
                existing_keys.add(unique_key)  # Track added key

            if len(batch) >= batch_size:
                existing_data[category].extend(batch)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=4, ensure_ascii=False)
                logging.info(f"✅ Saved {len(batch)} products to {output_file}")
                print(f"✅ Saved {len(batch)} products to {output_file}")
                batch = []

        if batch:
            existing_data[category].extend(batch)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            logging.info(f"✅ Saved {len(batch)} products to {output_file}")
            print(f"✅ Saved {len(batch)} products to {output_file}")