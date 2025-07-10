import os
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.connect import ConnectionParams

def get_weaviate_client():
    api_key = os.getenv("WEAVIATE_API_KEY")
    openai_key = os.getenv("OPENAI_APIKEY")
    http_host = os.getenv("WEAVIATE_URL")
    grpc_host = f"grpc-{http_host}"
    conn_params = ConnectionParams.from_params(
        http_host=http_host,
        http_port=443,
        http_secure=True,
        grpc_host=grpc_host,
        grpc_port=443,
        grpc_secure=True
    )
    client = weaviate.WeaviateClient(
        connection_params=conn_params,
        auth_client_secret=AuthApiKey(api_key),
        additional_headers={"X-OpenAI-Api-Key": openai_key}
    )
    client.connect()  # <--- required!
    return client
