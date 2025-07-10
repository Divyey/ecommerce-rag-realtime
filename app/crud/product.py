from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, cast, Float
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional

def get_product(db: Session, product_id: str) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()

def create_or_update_product(db: Session, product: ProductCreate) -> Product:
    db_product = db.query(Product).filter(Product.id == product.id).first()
    if db_product:
        for field, value in product.dict().items():
            setattr(db_product, field, value)
    else:
        db_product = Product(**product.dict())
        db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, db_product: Product, update_data: dict) -> Product:
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, db_product: Product):
    db.delete(db_product)
    db.commit()

def filter_products(
    db: Session,
    category: Optional[str],
    subcategory: Optional[str],
    min_price: Optional[float],
    max_price: Optional[float]
) -> List[Product]:
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if subcategory:
        query = query.filter(Product.subcategory == subcategory)
    if min_price is not None:
        query = query.filter(cast(Product.price, Float) >= min_price)
    if max_price is not None:
        query = query.filter(cast(Product.price, Float) <= max_price)
    return query.all()

def search_products(db: Session, q: str) -> List[Product]:
    # Simple case-insensitive search in name or description
    pattern = f"%{q.lower()}%"
    return db.query(Product).filter(
        or_(
            Product.name.ilike(pattern),
            Product.description.ilike(pattern)
        )
    ).all()
