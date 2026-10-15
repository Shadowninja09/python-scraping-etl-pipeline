
from sqlalchemy import text

from database.db_connection import db_engine
import hashlib


def generate_url_hash(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def add_url(url):
    query = text("""
        INSERT INTO scrape_url (url, url_hash, status, retry_count)
        VALUES (:url, :url_hash, 'PENDING', 0)
        ON CONFLICT (url_hash) DO NOTHING
    """)

    engine = db_engine()

    with engine.begin() as connection:
        result = connection.execute(query, {
            "url": url,
            "url_hash": generate_url_hash(url),
        })

    return result.rowcount == 1


def get_main_url():
    query = text("""
        SELECT url
        FROM main_url
        LIMIT 1
    """)

    engine = db_engine()

    with engine.connect() as connection:
        return connection.execute(query).scalar_one_or_none()


def get_pending_url():
    query = text("""
        SELECT id, url, retry_count
        FROM scrape_url
        WHERE status = 'PENDING'
        ORDER BY id
        LIMIT 1
    """)

    engine = db_engine()

    with engine.connect() as connection:
        row = connection.execute(query).mappings().first()
        return dict(row) if row else None


def seed_starting_url():
    url = get_main_url()

    if not url:
        print("No starting URL found in main_url.")
        return

    inserted = add_url(url)

    if inserted:
        print(f"Added starting URL to queue: {url}")
    else:
        print(f"URL already exists in queue: {url}")
