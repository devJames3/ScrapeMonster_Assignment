from extract_categories import extract_categories
from extract_products import extract_product_links, extract_product_details
from utils import remove_duplicates
# import pandas as pd
import logging
import json
import time

if __name__ == "__main__":
    url = "https://www.tops.co.th/en"
    total_product_count = 0
    max_workers = 10

    logging.basicConfig(filename="scraper.log", level=logging.INFO)
    logging.info("Scraping started...")

    # Step 1: Extract Categories and their subcategory links
    start_time = time.time()
    categories = extract_categories(url, max_workers)
    logging.info(f"✅ Extracted categories in {time.time() - start_time:.2f} seconds")

    if not categories:
        logging.error("❌ No categories found! Skipping product extraction...")
    else:
        # Step 2: Extract product links
        start_time = time.time()
        products = extract_product_links(categories, max_workers)
        logging.info(f"✅ Extracted product links in {time.time() - start_time:.2f} seconds")

        # Step 3: Extract full product details
        start_time = time.time()
        all_product_data = extract_product_details(products, max_workers)
        logging.info(f"✅ Extracted product details in {time.time() - start_time:.2f} seconds")

        # Step 4: Deduplicate products
        unique_all_product_data = remove_duplicates(all_product_data)

        for k, v in unique_all_product_data.items():
            total_product_count += len(v)

        # Step 5: Save results to JSON
        if unique_all_product_data:
            with open("products.json", "w", encoding="utf-8") as file:
                json.dump(unique_all_product_data, file, indent=4, ensure_ascii=False)
            print("✅ JSON file saved successfully!")
            logging.info("Scraping Completed...")
        else:
            logging.error("❌ Possible error during scraping...")

    print("\n✅ Total Products Count:", total_product_count)
