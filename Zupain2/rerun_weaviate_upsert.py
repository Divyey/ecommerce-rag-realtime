from Zupain2.zupain2 import process_product_fields
from Zupain2.weaviate_zupain import upsert_weaviate_product

import json

PRODUCTS_PATH = "Zupain2/results-9-july-25-12-50pm/products_with_id.json"

with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
    products = json.load(f)

for idx, product in enumerate(products, 1):
    processed = process_product_fields(product)
    print(f"Upserting product {idx}/{len(products)}: {processed.get('name')}")
    upsert_weaviate_product(processed)
