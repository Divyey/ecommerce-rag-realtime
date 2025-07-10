from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import openai

from app.core.weaviate_client import get_weaviate_client

router = APIRouter()

# OpenAI v1.x client instantiation
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AskRequest(BaseModel):
    question: str

class ProductContext(BaseModel):
    name: str
    description: str
    url: str
    price: str = ""  # Add price field, default to empty string

class AskResponse(BaseModel):
    answer: str
    products: List[ProductContext]

@router.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    question = req.question

    products = []
    try:
        client = get_weaviate_client()
        client.connect()
        try:
            collection = client.collections.get("Product")
            results = collection.query.near_text(
                query=question,
                limit=5
            )
            for obj in results.objects:
                props = obj.properties
                products.append(ProductContext(
                    name=str(props.get("name") or ""),
                    description=str(props.get("description") or ""),
                    url=str(props.get("url") or ""),
                    price=str(props.get("price") or "")
                ))
        finally:
            client.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weaviate error: {str(e)}")

    # Prepare context string for OpenAI prompt, including price
    context_text = "\n\n".join(
        [
            f"Name: {p.name}\nDescription: {p.description}\nPrice: {p.price}\nURL: {p.url}"
            for p in products
        ]
    ) or "No relevant product information found."

    prompt = f"""
You are a helpful assistant for an e-commerce platform.

Use the following product information to answer the question:

{context_text}

Question: {question}

Answer:
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    return AskResponse(answer=answer, products=products)
