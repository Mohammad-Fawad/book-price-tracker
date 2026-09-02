from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import get_book, get_books
from app.database import get_db
from app.schemas import BookResponse, PaginatedBooksResponse, ScrapeResponse
from app.scraper import scrape_books

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]


@router.get("/books", response_model=PaginatedBooksResponse)
def list_books(
    db: DBSession,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot be greater than max_price")

    total, items = get_books(
        db,
        page=page,
        limit=limit,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )
    return {"total": total, "page": page, "limit": limit, "items": items}


@router.get("/books/{book_id}", response_model=BookResponse)
def book_detail(book_id: int, db: DBSession):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/scrape", response_model=ScrapeResponse)
def trigger_scrape(db: DBSession):
    result = scrape_books(db)
    return {"message": "Scrape completed", **result}
