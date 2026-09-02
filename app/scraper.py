import os
from dotenv import load_dotenv

import logging
import requests

from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book


load_dotenv()


BASE_URL = os.getenv("BASE_URL")

SCRAPE_LIMIT = int(
    os.getenv("SCRAPE_LIMIT", "200")
)
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}
logger = logging.getLogger(__name__)

def get_soup(url):
    try:
        response = requests.get(
            url,
            timeout=10
        )
        response.raise_for_status()
        return BeautifulSoup(
            response.text,
            "html.parser"
        )
    except requests.RequestException as error:
        logger.error(
            "Could not load page %s: %s",
            url,
            error
        )
        return None

def get_book_details(
    book_url,
    page_number
):
    soup = get_soup(book_url)
    if soup is None:
        return None
    try:
        title_element = soup.select_one(
            "div.product_main h1"
        )
        if not title_element:
            return None
        title = title_element.get_text(
            strip=True
        )
        price_element = soup.select_one(
            "div.product_main p.price_color"
        )
        if not price_element:
            return None
        price_text = price_element.get_text(
            strip=True
        )
        price_text = (
            price_text
            .replace("£", "")
            .replace("Â", "")
            .strip()
        )
        price = Decimal(price_text)
        rating_element = soup.select_one(
            "div.product_main p.star-rating"
        )
        rating = None
        if rating_element:
            rating_classes = rating_element.get(
                "class",
                []
            )
            for rating_word, rating_number in RATING_MAP.items():

                if rating_word in rating_classes:

                    rating = rating_number
                    break
        if rating is None:
            return None
        availability_element = soup.select_one(
            "div.product_main p.availability"
        )
        if availability_element:
            availability = availability_element.get_text(
                " ",
                strip=True
            )
        else:
            availability = "Unknown"
        category_element = soup.select_one(
            "ul.breadcrumb li:nth-of-type(3) a"
        )
        if category_element:
            category = category_element.get_text(
                strip=True
            )
        else:
            category = "Unknown"
        return {
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category": category,
            "product_url": book_url,
            "page_number": page_number,
        }
    except Exception as error:
        logger.error(
            "Could not parse book %s: %s",
            book_url,
            error
        )
        return None

def save_book(
    db: Session,
    book_data
):
    existing_book = db.scalar(
        select(Book).where(
            Book.product_url
            == book_data["product_url"]
        )
    )
    if existing_book:
        existing_book.title = book_data["title"]
        existing_book.price = book_data["price"]
        existing_book.rating = book_data["rating"]
        existing_book.availability = book_data[
            "availability"
        ]
        existing_book.category = book_data[
            "category"
        ]
        existing_book.page_number = book_data[
            "page_number"
        ]
        existing_book.scraped_at = datetime.now(
            timezone.utc
        )
        return "updated"
    
    new_book = Book(
        title=book_data["title"],
        price=book_data["price"],
        rating=book_data["rating"],
        availability=book_data[
            "availability"
        ],
        category=book_data[
            "category"
        ],
        product_url=book_data[
            "product_url"
        ],
        page_number=book_data[
            "page_number"
        ],
    )
    db.add(new_book)
    return "created"

def scrape_books(
    db: Session,
    limit: int = SCRAPE_LIMIT
):
    created = 0
    updated = 0
    failed = 0
    discovered = 0
    processed = 0
    seen_urls = set()
    page_number = 1
    page_url = urljoin(
        BASE_URL,
        "catalogue/page-1.html"
    )
    while (
        page_url
        and processed < limit
    ):
        soup = get_soup(
            page_url
        )
        if soup is None:
            break
        book_cards = soup.select(
            "article.product_pod"
        )
        if not book_cards:
            break

        for book_card in book_cards:
            if processed >= limit:
                break
            link_element = book_card.select_one(
                "h3 a"
            )
            if not link_element:
                failed += 1
                continue
            relative_url = link_element.get(
                "href"
            )
            if not relative_url:
                failed += 1
                continue
            book_url = urljoin(
                page_url,
                relative_url
            )

            if book_url in seen_urls:
                continue
            seen_urls.add(
                book_url
            )
            discovered += 1
            try:
                book_data = get_book_details(
                    book_url,
                    page_number
                )
                if book_data is None:

                    failed += 1
                    continue

                result = save_book(
                    db,
                    book_data
                )

                db.commit()

                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1

                processed += 1

            except Exception as error:
                db.rollback()
                failed += 1
                logger.error(
                    "Failed to save book %s: %s",
                    book_url,
                    error
                )

        if processed >= limit:
            break

        next_button = soup.select_one(
            "li.next a"
        )
        if next_button:
            next_page = next_button.get(
                "href"
            )
            page_url = urljoin(
                page_url,
                next_page
            )
            page_number += 1

        else:
            page_url = None

    return {
        "discovered": discovered,
        "created": created,
        "updated": updated,
        "failed": failed,
    }

def main():
    from app.database import (
        Base,
        SessionLocal,
        engine
    )
    Base.metadata.create_all(
        bind=engine
    )
    db = SessionLocal()
    try:
        result = scrape_books(
            db
        )
        print("Scraping completed:")

        print(
            f"Discovered: {result['discovered']}"
        )

        print(
            f"Created: {result['created']}"
        )

        print(
            f"Updated: {result['updated']}"
        )

        print(
            f"Failed: {result['failed']}"
        )
    finally:
        db.close()

if __name__ == "__main__":
    main()