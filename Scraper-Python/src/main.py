from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.parse import urljoin
import json

import requests
from bs4 import BeautifulSoup

START_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/iamstevenflogio/Flyrank-Backend-Engineer-Internship)"
)
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5
MAX_CATALOGUE_PAGES = 3

def cache_path_for_catalogue_page(page_number: int) -> Path:
    return CACHE_DIR / f"catalogue-page-{page_number}.html"

def cache_path_for_book(book_url: str) -> Path:
    slug = book_url.rstrip("/").split("/")[-2]
    return CACHE_DIR / "books" / f"{slug}.html"

def fetch_and_cache(url: str, cache_file: Path) -> str:
    cache_file.parent.mkdir(parents=True, exist_ok=True)

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

    response.encoding = "utf-8"
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

def text_or_none(element) -> str | None:
    if element is None:
        return None

    text = element.get_text(" ", strip=True)
    return text or None

def extract_raw_book_record(
    detail_html: str,
    product_url: str, 
    source_page: str,
) -> dict:
    soup = BeautifulSoup(detail_html, "html.parser")
    product_main = soup.select_one("div.product_main")

    if product_main is None:
        raise ValueError(f"Could not find product area for {product_url}")

    title = text_or_none(product_main.select_one("h1"))
    price_text = text_or_none(product_main.select_one("p.price_color"))
    availability_text = text_or_none(product_main.select_one("p.availability"))
    rating_tag = product_main.select_one("p.star-rating")
    rating_text = None

    if rating_tag is not None:
        rating_classes = rating_tag.get("class", [])
        rating_text = next(
            (
                class_name
                for class_name in rating_classes
                if class_name != "star-rating"
            ),
            None,
        )

    description_heading = soup.select_one('#product_description')

    if description_heading is None:
        description = None
    else:
        description = text_or_none(description_heading.find_next("p"))

    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }

def extract_all_raw_records(book_urls: list[str]) -> list[dict]:
    raw_records = []

    for index, book_url in enumerate(book_urls, start=1):
        print(f"\nProcessing book {index}/{len(book_urls)}")
        book_cache_file = cache_path_for_book(book_url)

        detail_html = fetch_and_cache(book_url, book_cache_file)

        record = extract_raw_book_record(
            detail_html=detail_html,
            product_url=book_url,
            source_page=START_PAGE_URL,
        )

        raw_records.append(record)

    return raw_records

def main():
    book_urls = discover_catalogue_pages()
    raw_records = extract_all_raw_records(book_urls)

    print("\n--- Detail summary ---")
    print(f"detail_pages={len(raw_records)}")

    print("\nOne complete raw record")
    print(json.dumps(raw_records[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()