
from scraper.url_queue import seed_starting_url
from scraper.worker import process_one_url


def run_pipeline():
    print("Starting scraping pipeline...")

    seed_starting_url()

    while True:
        # The worker claims and processes the URL itself.
        result = process_one_url()

        if result is None:
            break

        print(
            f"Completed: {result['url']} | "
            f"Status: {result['status']}"
        )

    print("Scraping pipeline completed.")


if __name__ == "__main__":
    run_pipeline()
