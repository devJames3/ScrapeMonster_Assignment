# 🛍️ Web Scraping Assignment - Tops Online (ScrapeMonster.tech)

## **📌 Project Overview**

This project extracts product data from [Tops Online](https://www.tops.co.th/en), an e-commerce website, by navigating through categories and subcategories to scrape product details such as names, images, quantity, barcode, prices, and labels.

The script is optimized for:

- **Accuracy**: At least 95% match with website data
- **Efficiency**: Uses Selenium for JavaScript-rendered content and BeautifulSoup for fast parsing
- **Maintainability**: Modular functions with proper error handling

**_(Please read the `How to run the script` section properly to avoid system crash of memory issues")_**

---

## **📦 Extracted Data Fields**

For each product, the script extracts:

- **Product Name**
- **Product Images** (All available images)
- **Quantity** (e.g., `"500g"`, `"1L"`)
- **Barcode Number** (Valid EAN/UPC)
- **Product Details** (Full description)
- **Price** (Numerical value + currency)
- **Labels** (e.g., `"Plant-Based"`, `"Vegan"`, `"Best Seller"`)

---

## **⚙️ Installation**

### **1️⃣ Prerequisites**

Ensure you have the following installed:

- Python (>= 3.8)
- Google Chrome
- ChromeDriver

### **2️⃣ Install Dependencies**

Run the following command:

```bash
pip install -r requirements.txt
```

_(Make sure `requirements.txt` includes Selenium, BeautifulSoup, pandas, and lxml)_

---

## **🚀 How to Run the Script**

**_(Due to the size of the data to scrape, limit(optional) is added to fetch limited number of categories/products, remove limit to fetch all products - `extract_categories(url, max_workers, limit)`, `extract_product_links(categories, max_workers, limit)` called in `main.py`)_**

**_(Make sure `max_workers = ..` is set in the `main.py` file based on your system spec.If CPU is hitting 100% or RAM is nearly full, reduce max_workers)_**

```bash
python main.py
```

This will:

1. Navigate to the homepage.
2. Extract all **categories** and their subcategories.
3. Scrape **product data** from each subcategory.
4. Save the output in **JSON format**. `products.json` file

---

## **🛠️ Approach Used**

### **🔹 Category Extraction**

- **BeautifulSoup** parses and extracts categories from homepage

### **🔹 Subcategory Extraction**

- Selenium loads the page.
- **BeautifulSoup** parses and extracts subcategory links (`<a class="plp-carousel__link">`).
- This speeds up data extraction.

### **🔹 Product Extraction**

- Extracts products from listing pages.
- Handles **infinite scrolling** to ensure all products load.
- Extracts structured product details from `<div class="product-Details-page-root">`.

### **🔹 Data Processing & Export**

- Deduplicates products based on **name + SKU**.
- Standardizes **pricing format** (`{"value": 30.0, "currency": "THB"}`).
- Saves output as `products.json`

---

## **⚠️ Challenges & Solutions**

### **1️⃣ JavaScript-Rendered Content**

**Issue**: Some elements were not visible on page load.  
✅ **Solution**: Used `safe_get()` to retry until elements load.

### **2️⃣ Infinite Scrolling**

**Issue**: Some product listings required scrolling to load all products.  
✅ **Solution**: Used Selenium’s `execute_script("window.scrollTo(0, document.body.scrollHeight);")`.

---

## **📊 Sample Output (First Product)**

```json
{
  "OTOP": [
    {
      "productName": "(OTOP) Doikham Savoury Strawberry 30g.",
      "productImages": [
        "https://assets.tops.co.th/DOIKHAM-DoikhamSavouryStrawberry30g-8850773551115-2?$JPEG$",
        "https://assets.tops.co.th/DOIKHAM-DoikhamSavouryStrawberry30g-8850773551115-1?$JPEG$"
      ],
      "quantity": "30g",
      "barCodeNumber": "8850773551115",
      "productDetails": "Properties:\nThe product received may be subject to package modification...",
      "price": {
        "value": 30.0,
        "currency": "THB"
      },
      "label": "OTOP Product"
    }, {...}, {...}, ...
  ],
  "Only At Tops": [
    {
        "productName": "My Choice Golden Banana Pack",
        "productImages": [
            "https://assets.tops.co.th/MYCHOICE-MyChoiceGoldenBananaPack-8853474047505-1"
        ],
        "quantity": "N/A",
        "barCodeNumber": "8853474047505",
        "productDetails": "Properties:\nThe product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right...\n\nIngredients:\nN/A\n\nUsage:\nBring the whole banana to soak...\n\nDescription:\nN/A",
        "price": {
            "value": 39.0,
            "currency": "THB"
        },
        "label": "Best Seller"
    }, {...}, {...}, ...
  ],
  "Another_category": [{...}, {...}]
}
```

---

## **📊 Future improvements**

- Make the code more efficient and faster by adding batching in fetching sub-categories
- Pandas Dataframe implementations to help with data manipulation and modifications. As well ass data integrity checks.

---

🚀 **Built for Scrapemonster.tech** | Estonia 🇪🇪  
🔗 **Developed by James Okolie**
