from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, Text
from sqlalchemy.sql import func
from db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)  # cm
    weight = Column(Float, nullable=True)  # kg
    gender = Column(String, nullable=True)  # male / female / other
    activity = Column(Float, nullable=True)  # 1.2 - 1.9
    goal = Column(String, nullable=True)  # gain / maintain / lose
    calorie_goal = Column(Float, nullable=True)
    protein_goal = Column(Float, nullable=True)
    fat_goal = Column(Float, nullable=True)
    carb_goal = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
