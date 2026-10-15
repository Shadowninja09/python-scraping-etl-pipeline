
from bs4 import BeautifulSoup


def parse_quotes(html):
    soup = BeautifulSoup(html, "lxml")
    quotes = []

    for quote in soup.select("div.quote"):
        quote_text = quote.select_one("span.text")
        author = quote.select_one("small.author")
        tags = quote.select("div.tags a.tag")

        if not quote_text or not author:
            continue

        quotes.append({
            "quote_text": quote_text.get_text(strip=True),
            "author": author.get_text(strip=True),
            "tags": [tag.get_text(strip=True) for tag in tags],
        })

    return quotes
