from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class ProductBase(BaseModel):
    id: str
    url: Optional[str]
    name: Optional[str]
    price: Optional[str]
    old_price: Optional[str]
    discount: Optional[str]
    variant: Optional[str]
    sizes: Optional[List[str]]
    description: Optional[str]
    main_image: Optional[str]
    last_updated: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    video: Optional[str]
    seo_title: Optional[str]
    seo_description: Optional[str]

    model_config = ConfigDict(from_attributes=True)  # This is the v2+ way!

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    url: Optional[str]
    name: Optional[str]
    price: Optional[str]
    old_price: Optional[str]
    discount: Optional[str]
    variant: Optional[str]
    sizes: Optional[List[str]]
    description: Optional[str]
    main_image: Optional[str]
    last_updated: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    video: Optional[str]
    seo_title: Optional[str]
    seo_description: Optional[str]

    model_config = ConfigDict(from_attributes=True)
