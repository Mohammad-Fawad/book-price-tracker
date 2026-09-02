up:
	docker compose up --build

down:
	docker compose down

scrape:
	docker compose exec app python -m app.scraper
