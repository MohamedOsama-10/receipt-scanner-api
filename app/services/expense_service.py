from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import Optional
from datetime import date

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, data: ExpenseCreate, image_path: Optional[str] = None) -> Expense:
    expense = Expense(
        merchant=data.merchant,
        total=data.total,
        currency=data.currency,
        date=data.date,
        category=data.category,
        notes=data.notes,
        receipt_image_path=image_path,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    return db.query(Expense).filter(Expense.id == expense_id).first()


def list_expenses(
    db: Session,
    category: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Expense]:
    q = db.query(Expense)
    if category:
        q = q.filter(Expense.category == category)
    if year:
        q = q.filter(extract("year", Expense.date) == year)
    if month:
        q = q.filter(extract("month", Expense.date) == month)
    return q.order_by(Expense.created_at.desc()).offset(skip).limit(limit).all()


def update_expense(db: Session, expense_id: int, data: ExpenseUpdate) -> Optional[Expense]:
    expense = get_expense(db, expense_id)
    if not expense:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int) -> bool:
    expense = get_expense(db, expense_id)
    if not expense:
        return False
    db.delete(expense)
    db.commit()
    return True


def get_summary(db: Session, year: Optional[int] = None, month: Optional[int] = None) -> dict:
    """Return total spent per category for the given period."""
    q = db.query(Expense.category, func.sum(Expense.total).label("total"))
    if year:
        q = q.filter(extract("year", Expense.date) == year)
    if month:
        q = q.filter(extract("month", Expense.date) == month)
    rows = q.group_by(Expense.category).all()
    return {row.category: round(row.total or 0, 2) for row in rows}
