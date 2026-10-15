
from scraper.url_queue import seed_starting_url, get_pending_url

seed_starting_url()

url_record = get_pending_url()
print("Next pending URL:", url_record)
