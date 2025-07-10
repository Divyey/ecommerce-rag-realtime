from sqlalchemy import Column, Integer, String
from app.database import Base

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True, nullable=False)
    answer = Column(String, nullable=False)
