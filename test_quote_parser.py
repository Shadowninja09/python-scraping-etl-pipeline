
from scraper.request_handler import request_to_scrape
from scraper.quote_parser import parse_quotes
from database.quote_repository import save_quotes


url = "https://quotes.toscrape.com/"

response = request_to_scrape(url)

if response is None or response.status_code != 200:
    raise RuntimeError(f"Failed to fetch page: {url}")

quotes = parse_quotes(response.text)

print(f"Quotes extracted: {len(quotes)}")

if quotes:
    print("First quote:", quotes[0])

    inserted = save_quotes(quotes, url)
    print(f"New records inserted: {inserted}")
