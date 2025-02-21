from extract_categories import extract_categories
from extract_products import extract_product_links, extract_product_details

if __name__ == "__main__":
    url = "https://www.tops.co.th/en"
    
    general_data = {}

    # Step 1: Extract Categories and their appropriate subcategory links { "category_name": [ "sub_link1", "sub_link2", .... ], ...... }
    categories = extract_categories(url, 2)
    
    # Step 2: Extract product links from subcategory { "category_name": [ "product_link1", "product_link2", .... ], ...... }
    products = extract_product_links(categories, 2) 
    
    # # Step 3: Extract full details from each product page { "category_name": [  {"productName":"..", "productImages": [], "quantity": "..", .... } ], "another_category_name": [ {...}, {..}, ... ] ...... }
    # all_product_data = extract_product_details(products)
    # all_product_data = []
    # for link in product_links[:5]:  # Limit to first 5 products for testing
    #     product_details = extract_product_details(link)
    #     all_product_data.append(product_details)

    print("\n✅ Extracted Products:", products)


# if __name__ == "__main__":
#     test_subcategory_url = "https://www.tops.co.th/en/fruit-and-vegetables/grapes-cherries-berries"
    
#     # Step 1: Extract product links from subcategory
#     product_links = extract_product_links(test_subcategory_url)
    
#     # Step 2: Extract full details from each product page
#     all_product_data = []
#     for link in product_links[:5]:  # Limit to first 5 products for testing
#         product_details = extract_product_details(link)
#         all_product_data.append(product_details)

#     print("\n✅ Extracted Product Details:", all_product_data)