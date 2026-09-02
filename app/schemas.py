from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class BookResponse(BaseModel):
    id: int
    page_number: int
    title: str
    price: Decimal
    rating: int
    category: str
    availability: str
    product_url: str
    scraped_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaginatedBooksResponse(BaseModel):
    total: int
    books: list[BookResponse]


class ScrapeResponse(BaseModel):
    message: str
    discovered: int
    created: int
    updated: int
    failed: int