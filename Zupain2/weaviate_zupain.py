import os
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthApiKey

load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_weaviate_client():
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
        headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
        skip_init_checks=True
    )

def upsert_weaviate_product(product: dict):
    client = get_weaviate_client()
    class_name = "Product"
    uuid = product.get("id")
    if not uuid:
        print("Product missing 'id', skipping Weaviate upsert.")
        client.close()
        return

    allowed_fields = {
        "name", "category", "subcategory", "description", "main_image",
        "variant", "sizes", "url", "price", "old_price", "discount",
        "video", "seo_title", "seo_description"
    }
    clean_product = {k: v for k, v in product.items() if k in allowed_fields and v is not None}
    if "sizes" in clean_product and not isinstance(clean_product["sizes"], list):
        clean_product["sizes"] = [str(clean_product["sizes"])]
    elif "sizes" in clean_product:
        clean_product["sizes"] = [str(s) for s in clean_product["sizes"]]

    # Log the payload for debugging
    print(f"Upserting to Weaviate (uuid={uuid}): {clean_product}")

    try:
        client.collections.get(class_name).data.insert(
            uuid=uuid,
            properties=clean_product,
        )
        print(f"Upserted to Weaviate: {product.get('name')}")
    except Exception as e:
        print(f"Weaviate upsert error for {product.get('name')}: {e}")
    finally:
        client.close()
