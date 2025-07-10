import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from app.models.product import product
from app.core.weaviate_client import get_weaviate_client

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def sync_products():
    db = SessionLocal()
    client = get_weaviate_client()
    collection = client.collections.get("Product")
    products = db.query(Product).all()
    for p in products:
        props = {
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "variant": p.variant,
            "sizes": p.sizes,
            "main_image": p.main_image,
            "url": p.url,
        }
        collection.data.insert(properties=props, uuid=p.id)
    db.close()
    print(f"Synced {len(products)} products to Weaviate Cloud.")

if __name__ == "__main__":
    sync_products()
