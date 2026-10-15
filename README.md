# Python Scraping & ETL Pipeline

A modular Python web scraping and ETL project designed to demonstrate reliable data extraction, URL queue management, duplicate prevention, and PostgreSQL integration.

## Current Features

- HTTP requests with configurable retries and timeouts
- Randomized User-Agent selection
- HTML parsing using BeautifulSoup
- Pagination discovery and URL queue management
- PostgreSQL storage using SQLAlchemy
- Duplicate URL prevention using URL hashes
- Duplicate quote prevention using quote hashes
- Processing status tracking for scraped URLs

## Architecture

```text
main_url
   |
   v
URL Queue (PostgreSQL)
   |
   v
Request Handler
   |
   v
Quote Parser
   |
   v
Quote Repository
   |
   v
PostgreSQL (quote_data)
```

## Technology Stack

- Python
- Requests
- BeautifulSoup
- SQLAlchemy
- PostgreSQL
- Git

## Project Structure

```text
project/
├── database/
│   ├── db_connection.py
│   └── quote_repository.py
├── scraper/
│   ├── request_handler.py
│   ├── quote_parser.py
│   ├── url_queue.py
│   └── worker.py
├── pipeline/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Learning Target

The initial implementation uses [Quotes to Scrape](https://quotes.toscrape.com/) as a practice website.

## Planned Improvements

- Automatic retry scheduling and failure recovery
- Structured logging and execution metrics
- Automated tests
- Safe concurrent URL processing
- Pipeline orchestration
- Adaptation to additional data sources

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and configure your local PostgreSQL credentials.
5. Create the required database tables using the SQL definitions documented in the project.
6. Run the worker from the project root using `python -m scraper.worker`.

This project is under active development. Features will be added incrementally as the pipeline evolves.