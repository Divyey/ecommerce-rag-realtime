import os
import weaviate
from weaviate.auth import AuthApiKey

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,  # Hostname only, no https://
    auth_credentials=AuthApiKey(WEAVIATE_API_KEY),
    # Optionally: additional_headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
)

def get_weaviate_client():
    return client
