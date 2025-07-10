import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Configure, DataType
from dotenv import load_dotenv
import os

load_dotenv()
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
    skip_init_checks=True
)

# Delete old class if needed (CAUTION: deletes all Product data!)
if client.collections.exists("Product"):
    client.collections.delete("Product")

client.collections.create(
    name="Product",
    description="A product from Zupain",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    properties=[
        {"name": "name", "data_type": DataType.TEXT},
        {"name": "category", "data_type": DataType.TEXT},
        {"name": "subcategory", "data_type": DataType.TEXT},
        {"name": "description", "data_type": DataType.TEXT},
        {"name": "main_image", "data_type": DataType.TEXT},
        {"name": "variant", "data_type": DataType.TEXT},
        {"name": "sizes", "data_type": DataType.TEXT_ARRAY},
        {"name": "url", "data_type": DataType.TEXT},
        {"name": "price", "data_type": DataType.NUMBER},
        {"name": "old_price", "data_type": DataType.NUMBER},
        {"name": "discount", "data_type": DataType.NUMBER},
        {"name": "video", "data_type": DataType.TEXT},
        {"name": "seo_title", "data_type": DataType.TEXT},
        {"name": "seo_description", "data_type": DataType.TEXT},
    ]
)
client.close()
