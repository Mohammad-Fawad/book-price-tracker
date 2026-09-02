from datetime import datetime, timezone
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    page_number: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    index=True
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        index=True
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    availability: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    product_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True,
        index=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    __table_args__ = (

        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_rating_between_1_and_5"
        ),

        CheckConstraint(
            "price >= 0",
            name="check_price_positive"
        ),
    )