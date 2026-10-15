from request_handler import request_to_scrape
from bs4 import BeautifulSoup
from database.db_connection import db_engine, text


def get_main_url():
    engine = db_engine()
    connection = engine.connect()

    with connection as conn:
        result = conn.execute(text(" Select url from main_url"))
        
        url = result.mappings().first()

        if url:
            return url.get('url')

        return None
        


def parser():
    url = get_main_url()

    if not url:
        print("No URL found.")
        return

    try:
        response = request_to_scrape(url)

        if response is None:
            print("Request failed: No response received.")
            return

        # Handle HTTP status codes
        if response.status_code == 404:
            print(f"Page not found: {url}")
            return

        if response.status_code != 200:
            print(f"Request failed with status: {response.status_code}")
            return

        # Validate response size
        length = len(response.content)
        minimum_response_length = 200

        if length <= minimum_response_length:
            print(f"Response too small: {length} bytes")
            return

        # Parse HTML
        soup = BeautifulSoup(response.content, "lxml")
        next_url = soup.find("li", {"class": "next"})
        print(next_url)

    except Exception as exc:
        print(f"Parser failed: {exc}")


parser()

