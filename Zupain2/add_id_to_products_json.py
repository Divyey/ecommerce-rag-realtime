import json
import uuid

INPUT_PATH = "Zupain2/results-9-july-25-12-50pm/products.json"
OUTPUT_PATH = "Zupain2/results-9-july-25-12-50pm/products_with_id.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    products = json.load(f)

for product in products:
    # Use URL as the basis for a repeatable UUID
    if 'url' in product and product['url']:
        product['id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, product['url']))
    else:
        product['id'] = str(uuid.uuid4())

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2)

print(f"Added 'id' to {len(products)} products. Saved to {OUTPUT_PATH}")
