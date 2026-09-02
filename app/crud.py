from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Book

def get_books(
    db: Session,
    page: int | None = None,
    book_id: int | None = None,
    category: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
):
    if book_id is not None:
        query = select(Book).where(
            Book.id == book_id
        )
        return db.scalar(query)
    
    query = select(Book)

    if category is not None:

        query = query.where(
            func.lower(Book.category)
            == category.strip().lower()
        )

    if (
        min_price is not None
        and max_price is not None
    ):
        query = query.where(
            Book.price >= min_price,
            Book.price <= max_price
        )

    if page is not None:
        query = query.where(
            Book.page_number == page
        )
    query = query.order_by(Book.id)

    books = db.scalars(query).all()

    total = len(books)

    return books, total