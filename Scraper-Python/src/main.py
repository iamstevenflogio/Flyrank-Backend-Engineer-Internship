from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")

USER_AGENT = (
    "FlyRankInternshipA9/1.0"
    "(+https://github.com/iamstevenflogio/Flyrank-Backend-Engineer-Internship)"
)
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5
MAX_CATALOGUE_PAGES = 3

def cache_path_for_catalogue_page(page_number: int) -> Path:
    return CACHE_DIR / f"catalogue-page-{page_number}.html"

def fetch_and_cache(url: str, cache_file: Path) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT size_bytes={len(html.encode('utf-8'))}")
        return html

    sleep(REQUEST_DELAY_SECONDS)

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)

    if response.status_code != 200:
        raise RuntimeError(
            f"Fetch failed with status code={response.status_code} url={url}"
        )

    html = response.text
    cache_file.write_text(html, encoding="utf-8")
    print(f"FETCH size_bytes={len(html.encode('utf-8'))}")
    return html

def extract_book_urls(html: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    book_links = soup.select("article.product_pod h3 a")
    urls = []

    for link in book_links:
        href = link.get("href")

        if href:
            absolute_url = urljoin(page_url, href)
            urls.append(absolute_url)
            
    return urls

def extract_next_page_url(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href" )

    if not href:
        return None

    return urljoin(page_url, href)

def discover_catalogue_pages() -> list[str]:
    current_url = START_PAGE_URL
    discovered_urls = []
    catalogue_pages_processed = 0

    while current_url is not None and catalogue_pages_processed < MAX_CATALOGUE_PAGES:
        page_number = catalogue_pages_processed + 1
        cache_file = cache_path_for_catalogue_page(page_number)

        print(f"\nProcessing catalogue page {page_number}")
        html = fetch_and_cache(current_url, cache_file)

        page_book_urls = extract_book_urls(html, current_url)
        discovered_urls.extend(page_book_urls)

        catalogue_pages_processed += 1
        current_url = extract_next_page_url(html, current_url)

    unique_urls = sorted(set(discovered_urls))

    print("\n--- Discovery summary ---")
    print(f"catalogue_pages={catalogue_pages_processed}")
    print(f"discovered={len(discovered_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls

def main():
    book_urls = discover_catalogue_pages()

    print("\nFirst 3 book URLs:")
    for url in book_urls[:3]:
        print(url)

if __name__ == "__main__":
    main()