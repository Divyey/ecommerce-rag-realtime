from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.database import Base
import enum
from datetime import datetime
from sqlalchemy.orm import relationship

class UserRole(enum.Enum):
    admin = "admin"
    seller = "seller"
    customer = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # products = relationship("Product", back_populates="seller")