from extract_categories import extract_categories
from extract_products import extract_product_links, extract_product_details
from utils import remove_duplicates
import pandas as pd
import logging
import json

if __name__ == "__main__":
    url = "https://www.tops.co.th/en"
    total_product_count = 0

    logging.basicConfig(filename="scraper.log", level=logging.INFO)
    logging.info("Scraping started...")
    logging.info("Extracting product categories...")
    # Step 1: Extract Categories and their appropriate subcategory links { "category_name": [ "sub_link1", "sub_link2", .... ], ...... }
    categories = extract_categories(url, 2)
    
    logging.info("Extracting products...")
    # Step 2: Extract product links from subcategory { "category_name": [ "product_link1", "product_link2", .... ], ...... }
    products = extract_product_links(categories, 2) 
    
    logging.info("Extracting products details...")
    # Step 3: Extract full details from each product page { "category_name": [  {"productName":"..", "productImages": [], "quantity": "..", .... } ], "another_category_name": [ {...}, {..}, ... ] ...... }
    all_product_data = extract_product_details(products)

    # Step 4: Deduplicate products (based on name + SKU)
    unique_all_product_data = remove_duplicates(all_product_data)

    for k, v in unique_all_product_data.items():
        product_count = len(v)
        total_product_count = total_product_count + product_count

    logging.info("Writing to JSON file...")
    # Writing to JSON file
    if unique_all_product_data:
        with open("products.json", "w", encoding="utf-8") as file:
            json.dump(unique_all_product_data, file, indent=4, ensure_ascii=False)
        print("✅ JSON file saved successfully!")
        logging.info("Scraping Completed...")
    else:
        logging.info("Possible error during scraping...")
        


    # print("\n✅ Extracted Products:", unique_all_product_data)
    print("\n✅ Total Products Count: ", total_product_count)