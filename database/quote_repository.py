
import hashlib

from sqlalchemy import text

from database.db_connection import db_engine


def generate_quote_hash(quote_text, author):
    unique_value = f"{quote_text.strip()}|{author.strip()}"
    return hashlib.sha256(unique_value.encode("utf-8")).hexdigest()


def save_quotes(quotes, source_url):
    if not quotes:
        return 0

    query = text("""
        INSERT INTO quote_data (
            quote_text,
            author,
            tags,
            source_url,
            quote_hash
        )
        VALUES (
            :quote_text,
            :author,
            :tags,
            :source_url,
            :quote_hash
        )
        ON CONFLICT (quote_hash) DO NOTHING
    """)

    records = []

    for quote in quotes:
        records.append({
            "quote_text": quote["quote_text"],
            "author": quote["author"],
            "tags": quote["tags"],
            "source_url": source_url,
            "quote_hash": generate_quote_hash(
                quote["quote_text"],
                quote["author"]
            ),
        })

    engine = db_engine()

    with engine.begin() as connection:
        result = connection.execute(query, records)

    return result.rowcount
