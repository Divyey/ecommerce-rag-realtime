# app/models/product.py
from sqlalchemy import Column, String, Integer, Text, JSON
from app.database import Base

class Product(Base):
    __tablename__ = "products"  # or "zupain_data" if that's your table
    id = Column(String, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(String)
    old_price = Column(String)
    discount = Column(String)
    variant = Column(String)
    sizes = Column(JSON)
    description = Column(Text)
    main_image = Column(String)
    last_updated = Column(String)
    category = Column(String)
    subcategory = Column(String)
    video = Column(String)
    seo_title = Column(String)
    seo_description = Column(String)