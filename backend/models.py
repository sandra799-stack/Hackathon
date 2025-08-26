from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app_db import Base  # <-- use the same Base!

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(120), unique=True, nullable=False)
    promotion_name = Column(String(50), unique=True, nullable=False)
    active_promotions = relationship("ActivePromotion", back_populates="promotion")


class ActivePromotion(Base):
    __tablename__ = "active_promotions"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(100), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False)
    promotion = relationship("Promotion", back_populates="active_promotions")
