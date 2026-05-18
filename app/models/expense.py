from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    # Core receipt data
    merchant = Column(String(255), nullable=True)
    total = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="USD")
    date = Column(Date, nullable=True)

    # Classification
    category = Column(String(100), nullable=False, default="Other")

    # Optional extra info
    notes = Column(Text, nullable=True)
    receipt_image_path = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Expense id={self.id} merchant={self.merchant} total={self.total} {self.currency}>"
