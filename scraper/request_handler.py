import requests
import time
import random


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
]

def request_to_scrape(url, max_retries=5, base_delay=2, max_delay=30):

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="155", "Chromium";v="155", "Not(A:Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        "User-Agent": random.choice(USER_AGENTS),
    }

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            status = response.status_code

            # Success
            if status == 200:
                return response

            # Exit immediately for 404
            if status == 404:
                print(f"404 Not Found: {url}")
                return response

            # Retry only selected status codes
            if status not in (429, 403, 500, 502, 503, 504):
                return response

            # No more retries
            if attempt == max_retries:
                print(f"Retries exhausted. Last status: {status}")
                return response

            # Exponential backoff: 2, 4, 8, 16, 32 seconds
            wait = min(base_delay * (2 ** attempt), max_delay)

            # Honor Retry-After for 429 if available
            if status == 429:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    try:
                        wait = min(float(retry_after), max_delay)
                    except ValueError:
                        pass  # Use exponential backoff if header is invalid

            print(
                f"HTTP {status}. "
                f"Retry {attempt + 1}/{max_retries} "
                f"after {wait:.1f} seconds"
            )

            time.sleep(wait)

        except requests.exceptions.RequestException as exc:
            if attempt == max_retries:
                raise

            wait = min(base_delay * (2 ** attempt), max_delay)

            print(
                f"Request error: {exc}. "
                f"Retry {attempt + 1}/{max_retries} "
                f"after {wait:.1f} seconds"
            )

            time.sleep(wait)

    return None