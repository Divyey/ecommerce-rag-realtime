from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base
from datetime import datetime

class UpdateLog(Base):
    __tablename__ = "update_logs"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id")) 
    # product_id = Column(Integer, ForeignKey("products.id"))
    change_type = Column(String(50))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
    