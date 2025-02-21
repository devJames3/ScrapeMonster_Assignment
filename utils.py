import re
import time
from bs4 import BeautifulSoup
from stdnum import ean

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
    sku = sku.strip()  # Remove any extra spaces
    if not sku.isdigit():
        return False  # Must contain only digits
    
    # Validate using the library
    return ean.is_valid(sku)

def extract_paragraphs_with_newlines(div):
    """Extract all <p> tags from a div, preserving <br> tags as new lines."""
    paragraphs = div.find_all("p")
    
    extracted_text = []
    for p in paragraphs:
        text = p.get_text(separator="\n", strip=True)  # Ensure <br> becomes \n
        extracted_text.append(text)
    
    return "\n".join(extracted_text)  # Separate paragraphs with double newlines