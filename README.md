## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- BeautifulSoup
- Requests
- Docker
- Docker Compose

## Project Structure

book-price-tracker/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ ├── schemas.py
│ ├── crud.py
│ └── scraper.py
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

## Prerequisites

Make sure the following are installed:

- Docker Desktop
- Docker Compose
- Git

Python and PostgreSQL do not need to be installed separately when running the project with Docker.

## Setup and Run

### 1. Clone the repository

git clone <your-github-repository-url>
cd book-price-tracker

### 2. Create the environment file

Create a `.env` file in the project root.
Example:

```env
POSTGRES_USER=bookuser
POSTGRES_PASSWORD=bookpassword123
POSTGRES_DB=booktracker
BASE_URL=https://books.toscrape.com/
SCRAPE_LIMIT=200
```

### 3. Build and start the containers

docker compose up --build
This starts:

- the FastAPI application
- the PostgreSQL database

### 4. Check container status

docker compose ps
The database should be healthy and the application should be running.

### 5. Open the API documentation

http://localhost:8000/docs

## Running the Scraper

The scraper can be run in two ways.

### Option 1: Run the scraper independently

```bash
docker compose exec app python -m app.scraper
```

Example output:
Scraping completed:
Discovered: 200
Created: 200
Updated: 0
Failed: 0

Running the scraper again updates existing records instead of creating duplicates.
Example:

```text
Scraping completed:
Discovered: 200
Created: 0
Updated: 200
Failed: 0
```

### Option 2: Trigger the scraper through the API

```bash
curl -X POST http://localhost:8000/scrape
```

Example response:

json
{
"message": "Scraping completed successfully.",
"discovered": 200,
"created": 200,
"updated": 0,
"failed": 0
}

## API Endpoints

### GET `/books`

Returns all books when no query parameters are provided.
Example:

```bash
curl http://localhost:8000/books
```

Example response structure:

```json
{
  "total": 200,
  "books": [
    {
      "id": 1,
      "title": "A Light in the Attic",
      "price": "51.77",
      "rating": 3,
      "category": "Poetry",
      "availability": "In stock",
      "product_url": "https://books.toscrape.com/...",
      "page_number": 1,
      "scraped_at": "2026-09-03T00:00:00+00:00"
    }
  ]
}
```

### GET `/books?page={page_number}`

Returns all books stored for the requested source page.
books to Scrape contains 20 books per catalogue page.
Example:"http://localhost:8000/books?page=2"
This returns all books where: page_number = 2

### GET `/books/{id}`

Returns a single book by ID.
Example: http://localhost:8000/books/21
If the book does not exist:

```json
{
  "detail": "Book not found"
}
```

### GET `/books?category=xyz`

Filters books by category.
Example:"http://localhost:8000/books?category=Poetry"
Category matching is case-insensitive.

### GET `/books?min_price=X&max_price=Y`

Filters books by price range.
Example:

```bash
curl "http://localhost:8000/books?min_price=10&max_price=30"
```

This returns books where:
price >= 10
price <= 30
Both `min_price` and `max_price` must be supplied together.

### POST `/scrape`

Runs the scraper and updates the database.
Example:

```bash
curl -X POST http://localhost:8000/scrape
```

Example response:

```json
{
  "message": "Scraping completed successfully.",
  "discovered": 200,
  "created": 0,
  "updated": 200,
  "failed": 0
}
```

## Endpoint Summary

| Method | Endpoint | Description |
| GET | `/books` | Return all books |
| GET | `/books?page=2` | Return books from source page 2 |
| GET | `/books/{id}` | Return one book by ID |
| GET | `/books?category=xyz` | Filter books by category |
| GET | `/books?min_price=X&max_price=Y` | Filter books by price range |
| POST | `/scrape` | Run the scraper and update the database |

## Stored Book Data

Each book contains:

- ID
- Title
- Price
- Rating
- Category
- Availability
- Product URL
- Source page number
- Scraped timestamp

## Duplicate Handling

The `product_url` is used to identify an existing book.

When the scraper runs:

- a new product URL creates a new record
- an existing product URL updates the existing record
- repeated runs do not create duplicate books

## Stop the Project

Stop the containers:

```bash
docker compose down
```

The PostgreSQL data remains in the Docker volume.

To stop the project and remove the database volume:
docker compose down -v
