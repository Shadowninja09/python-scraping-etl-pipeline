
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from sqlalchemy import text

from database.db_connection import db_engine
from database.quote_repository import save_quotes
from scraper.request_handler import request_to_scrape
from scraper.quote_parser import parse_quotes
from scraper.url_queue import get_pending_url, add_url
from requests.exceptions import RequestException


MAX_FAILED_ATTEMPTS = 3

RETRYABLE_HTTP_STATUSES = {
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}


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
        return None

    url_id = url_record["id"]
    url = url_record["url"]
    previous_retry_count = url_record["retry_count"]
    http_status = None

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

        quotes = parse_quotes(response.text)

        inserted_count = save_quotes(quotes, url)

        next_url = find_next_page(response.text, url)

        if next_url:
            add_url(next_url)
            print(f"Next page discovered: {next_url}")
        else:
            print("No next page found.")

        update_url_status(
            url_id,
            status="SUCCESS",
            http_status=http_status,
        )

        print(f"Quotes parsed: {len(quotes)}")
        print(f"New quotes inserted: {inserted_count}")
        print(f"Successfully processed: {url}")

        return {
            "url": url,
            "status": "SUCCESS",
            "quotes_parsed": len(quotes),
            "quotes_inserted": inserted_count,
            "next_url": next_url,
        }

    except Exception as exc:
        # Decide whether this failure is worth retrying.
        retryable = (
            http_status in RETRYABLE_HTTP_STATUSES
            or isinstance(exc, RequestException)
        )

        # Count this failed worker attempt.
        failed_attempts = previous_retry_count + 1

        if retryable and failed_attempts < MAX_FAILED_ATTEMPTS:
            next_status = "PENDING"
        else:
            next_status = "FAILED"

        update_url_status(
            url_id,
            status=next_status,
            http_status=http_status,
            failed=True,
        )

        print(
            f"Failed to process {url}: {exc}. "
            f"Failed attempts: {failed_attempts}/"
            f"{MAX_FAILED_ATTEMPTS}. "
            f"Next status: {next_status}"
        )

        return {
            "url": url,
            "status": next_status,
            "quotes_parsed": 0,
            "quotes_inserted": 0,
            "next_url": None,
            "error": str(exc),
        }

