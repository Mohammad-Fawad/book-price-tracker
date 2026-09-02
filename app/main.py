from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.database import (
    Base,
    engine,
    get_db,
)
from app.crud import get_books

from app.schemas import (
    BookResponse,
    PaginatedBooksResponse,
    ScrapeResponse,
)

from app.scraper import scrape_books

@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(
        bind=engine
    )

    yield

app = FastAPI(
    title="Book Price Tracker API",
    description="API for tracking book information from books.toscrape.com",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get(
    "/books",
    response_model=PaginatedBooksResponse
)
def list_books(

    page: int | None = Query(
        default=None,
        ge=1
    ),
    category: str | None = Query(
        default=None
    ),
    min_price: Decimal | None = Query(
        default=None,
        ge=0
    ),

    max_price: Decimal | None = Query(
        default=None,
        ge=0
    ),
    db: Session = Depends(get_db)
):

    if (
        min_price is None
        and max_price is not None
    ) or (
        min_price is not None
        and max_price is None
    ):

        raise HTTPException(
            status_code=400,
            detail="Both min_price and max_price are required"
        )

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):

        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price"
        )

    books, total = get_books(
        db=db,
        page=page,
        category=category,
        min_price=min_price,
        max_price=max_price
    )

    return {
        "page": page,
        "total": total,
        "books": books
    }

@app.get(
    "/books/{book_id}",
    response_model=BookResponse
)
def get_single_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    if book_id < 1:
        raise HTTPException(
            status_code=400,
            detail="book_id must be greater than 0"
        )

    book = get_books(
        db=db,
        book_id=book_id
    )

    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book

@app.post(
    "/scrape",
    response_model=ScrapeResponse
)
def trigger_scrape(

    db: Session = Depends(get_db)
):

    try:

        result = scrape_books(
            db
        )
        return {
            "message": "Scraping completed successfully.",
            "discovered": result["discovered"],
            "created": result["created"],
            "updated": result["updated"],
            "failed": result["failed"],
        }
    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(error)}"
        )