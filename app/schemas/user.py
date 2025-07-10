from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
