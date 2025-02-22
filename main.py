from extract_categories import extract_categories
from extract_products import extract_product_links, extract_product_details
import logging
import time

if __name__ == "__main__":
    url = "https://www.tops.co.th/en"
    max_workers = 10

    logging.basicConfig(filename="scraper.log", level=logging.INFO)
    logging.info("Scraping started...")

    # Extract Categories
    start_time = time.time()
    categories = extract_categories(url, max_workers, 5)
    logging.info(f"✅ Extracted categories in {time.time() - start_time:.2f} seconds")

    if not categories:
        logging.error("❌ No categories found! Skipping product extraction...")
    else:
        # Extract product links
        start_time = time.time()
        products = extract_product_links(categories, max_workers, 5)
        logging.info(f"✅ Extracted product links in {time.time() - start_time:.2f} seconds")

        # Extract full product details (with deduplication)
        start_time = time.time()
        extract_product_details(products, max_workers, batch_size=50)
        logging.info(f"✅ Extracted product details in {time.time() - start_time:.2f} seconds")

    print("\n✅ Scraping Complete!")
