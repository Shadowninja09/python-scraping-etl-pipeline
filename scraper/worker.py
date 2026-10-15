
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy import text

from database.db_connection import db_engine
from database.quote_repository import save_quotes
from scraper.request_handler import request_to_scrape
from scraper.quote_parser import parse_quotes
from scraper.url_queue import get_pending_url, add_url


def update_url_status(url_id, status, http_status=None, failed=False):
    query = text("""
        UPDATE scrape_url
        SET status = :status,
            http_status = :http_status,
            retry_count = retry_count + :failed,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :url_id
    """)

    engine = db_engine()

    with engine.begin() as connection:
        connection.execute(query, {
            "url_id": url_id,
            "status": status,
            "http_status": http_status,
            "failed": int(failed),
        })


def find_next_page(html, current_url):
    soup = BeautifulSoup(html, "lxml")
    next_link = soup.select_one("li.next a")

    if not next_link:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return urljoin(current_url, href)


def process_one_url():
    url_record = get_pending_url()

    if not url_record:
        print("No pending URLs found.")
        return

    url_id = url_record["id"]
    url = url_record["url"]
    http_status = None

    engine = db_engine()

    # Mark the URL as currently being processed.
    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE scrape_url
                SET status = 'PROCESSING',
                    last_attempt_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :url_id
                  AND status = 'PENDING'
            """),
            {"url_id": url_id},
        )

    try:
        print(f"Processing URL: {url}")

        response = request_to_scrape(url)

        if response is None:
            raise RuntimeError("Request returned no response.")

        http_status = response.status_code

        if http_status != 200:
            raise RuntimeError(
                f"Unexpected HTTP status: {http_status}"
            )

        # Extract quotes from the page.
        quotes = parse_quotes(response.text)

        # Save quotes before marking the URL successful.
        inserted_count = save_quotes(quotes, url)

        # Discover and queue the next page, if one exists.
        next_url = find_next_page(response.text, url)

        if next_url:
            add_url(next_url)
            print(f"Next page discovered: {next_url}")
        else:
            print("No next page found.")

        # Mark success only after processing is complete.
        update_url_status(
            url_id,
            status="SUCCESS",
            http_status=http_status,
        )

        print(f"Quotes parsed: {len(quotes)}")
        print(f"New quotes inserted: {inserted_count}")
        print(f"Successfully processed: {url}")

    except Exception as exc:
        update_url_status(
            url_id,
            status="FAILED",
            http_status=http_status,
            failed=True,
        )

        print(f"Failed to process {url}: {exc}")


if __name__ == "__main__":
    process_one_url()
