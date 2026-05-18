from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import date, datetime


CATEGORIES = Literal[
    "Food & Drinks",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Entertainment",
    "Health",
    "Travel",
    "Other",
]


class ExpenseBase(BaseModel):
    merchant: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = "USD"
    date: Optional[date] = None
    category: CATEGORIES = "Other"
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Used when creating an expense manually or after scanning."""
    pass


class ExpenseUpdate(BaseModel):
    """All fields optional for partial updates."""
    merchant: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    date: Optional[date] = None
    category: Optional[CATEGORIES] = None
    notes: Optional[str] = None


class ExpenseOut(ExpenseBase):
    id: int
    receipt_image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LineItem(BaseModel):
    """A single line item from a receipt."""
    name: str
    price: Optional[float] = None


class ScanResult(BaseModel):
    """Raw output from the AI scanner before saving."""
    merchant: Optional[str] = None
    date: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    category: CATEGORIES = "Other"
    items: List[LineItem] = []

    model_config = {"from_attributes": True}
