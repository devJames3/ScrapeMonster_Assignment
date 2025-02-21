from extract_categories import extract_categories
from extract_products import extract_product_links, extract_product_details
from utils import remove_duplicates

if __name__ == "__main__":
    url = "https://www.tops.co.th/en"

    # Step 1: Extract Categories and their appropriate subcategory links { "category_name": [ "sub_link1", "sub_link2", .... ], ...... }
    categories = extract_categories(url, 2)
    
    # Step 2: Extract product links from subcategory { "category_name": [ "product_link1", "product_link2", .... ], ...... }
    products = extract_product_links(categories, 2) 
    
    # Step 3: Extract full details from each product page { "category_name": [  {"productName":"..", "productImages": [], "quantity": "..", .... } ], "another_category_name": [ {...}, {..}, ... ] ...... }
    all_product_data = extract_product_details(products)

    # Step 4: Deduplicate products (based on name + SKU)
    unique_all_product_data = remove_duplicates(all_product_data)

    print("\n✅ Extracted Products:", unique_all_product_data)