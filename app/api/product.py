from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import openai
import weaviate
from weaviate.auth import AuthApiKey

router = APIRouter()

# Load OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Weaviate Cloud client setup (v4)
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),  # Hostname only!
    auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    # Optionally: additional_headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")},
)


class AskRequest(BaseModel):
    question: str

class ProductContext(BaseModel):
    name: str
    description: str
    url: str

class AskResponse(BaseModel):
    answer: str
    products: List[ProductContext]

@router.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    question = req.question

    # 1. Query Weaviate for relevant products (top 5, semantic search)
    products = []
    try:
        collection = client.collections.get("Product")
        results = collection.query.near_text(
            query=question,
            limit=5
        )
        for obj in results.objects:
            props = obj.properties
            products.append(ProductContext(
                name=props.get("name", ""),
                description=props.get("description", ""),
                url=props.get("url", "")
            ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weaviate error: {str(e)}")

    # 2. Prepare context string for OpenAI prompt
    context_text = "\n\n".join(
        [f"Name: {p.name}\nDescription: {p.description}\nURL: {p.url}" for p in products]
    ) or "No relevant product information found."

    # 3. Build prompt for OpenAI
    prompt = f"""
You are a helpful assistant for an e-commerce platform.

Use the following product information to answer the question:

{context_text}

Question: {question}

Answer:
"""

    # 4. Call OpenAI ChatCompletion API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    return AskResponse(answer=answer, products=products)
