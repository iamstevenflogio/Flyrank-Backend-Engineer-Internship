from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter, sleep
from urllib.parse import urljoin
import json
import re 
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError
from requests.exceptions import RequestException, Timeout


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

OUTPUT_DIR = Path("output")
RUN_STATS = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "failed_pages": [],
}

class BookRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    product_url: HttpUrl
    price_text: str = Field(min_length=1)
    price_gbp: float = Field(ge=0)
    availability_text: str = Field(min_length=1)
    rating_text: str = Field(min_length=1)
    description: str | None = None
    source_page: HttpUrl
    fetched_at: datetime

def cache_path_for_catalogue_page(page_number: int) -> Path:
    return CACHE_DIR / f"catalogue-page-{page_number}.html"

def cache_path_for_book(book_url: str) -> Path:
    slug = book_url.rstrip("/").split("/")[-2]
    return CACHE_DIR / "books" / f"{slug}.html"

def fetch_and_cache(url: str, cache_file: Path) -> str:
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        RUN_STATS["cache_hits"] += 1
        print(f"CACHE HIT size_bytes={len(html.encode('utf-8'))}")
        return html

    headers = {"User-Agent": USER_AGENT}

    for attempt in range(1, 3):
        try:
            sleep(REQUEST_DELAY_SECONDS)

            response = requests.get(
                url, 
                headers=headers,
                timeout=TIMEOUT_SECONDS
            )

            if response.status_code == 200:
                response.encoding = "utf-8"
                html = response.text

                cache_file.write_text(html, encoding="utf-8")
                RUN_STATS["pages_fetched"] += 1
                print(f"FETCH size_bytes={len(html.encode('utf-8'))}")
                return html

            if response.status_code in {403, 404}:
                raise RuntimeError(
                    f"Fetch failed: status_code={response.status_code} url={url}"
                )

            if 500 <= response.status_code <= 599 and attempt == 1:
                print(
                    f"RETRY status_code={response.status_code} "
                    f"attempt={attempt} url={url}"
                )
                sleep(1)
                continue

            raise RuntimeError(
                f"Fetch failed: status_code={response.status_code} url={url}"
            )

        except Timeout:
            if attempt == 1:
                print(f"RETRY timeout attempt={attempt} url={url}")
                sleep(1)
                continue

            raise RuntimeError(f"Fetch failed after timeout url={url}")

        except RequestException as error:
            raise RuntimeError(f"Request failed url={url}: {error}") from error


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

        try:
            detail_html = fetch_and_cache(book_url, book_cache_file)

            record = extract_raw_book_record(
                detail_html=detail_html,
                product_url=book_url,
                source_page=START_PAGE_URL,
            )

            raw_records.append(record)

        except (RuntimeError, ValueError) as error:
            RUN_STATS["failed_pages"].append(
                {
                    "url": book_url,
                    "reason": str(error),
                }
            )
            print(f"SKIP url={book_url} reason={error}")

    return raw_records

def write_run_report(
    started_at: datetime,
    duration_seconds: float,
    valid_records: list[dict],
    invalid_records: list[dict],
) -> None:
    report = {
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round(duration_seconds, 2),
        "pages_fetched": RUN_STATS["pages_fetched"],
        "cache_hits": RUN_STATS["cache_hits"],
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "failed_pages": len(RUN_STATS["failed_pages"]),
        "failures": RUN_STATS["failed_pages"],
    }

    report_file = OUTPUT_DIR / "run-report.json"
    report_file.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def normalize_price(price_text: str) -> float:
    cleaned = price_text.replace("£", "").strip()

    if not re.fullmatch(r"\d+(\.\d{2})?", cleaned):
        raise ValueError(f"Invalid GBP price text: {price_text!r}")

    return float(cleaned) 

def normalize_raw_record(raw_record: dict[str, Any]) -> dict[str, Any]:
    normalized = raw_record.copy()
    normalized["price_gbp"] = normalize_price(raw_record["price_text"])
    return normalized

def validate_and_store_records(raw_records: list[dict],) -> tuple[list[dict], list[dict]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    valid_by_url: dict[str, dict] = {}
    errors = []

    for raw_record in raw_records:
        try:
            normalized = normalize_raw_record(raw_record)
            validated = BookRecord.model_validate(normalized)

            record = validated.model_dump(mode="json")
            valid_by_url[record["product_url"]] = record

        except (ValueError, ValidationError) as error:
            errors.append(
                {
                    "product_url": raw_record.get("product_url"),
                    "reason": str(error),
                    "raw_record": raw_record
                }
            )

    valid_records = list(valid_by_url.values())

    books_file = OUTPUT_DIR / "books.json"
    errors_file = OUTPUT_DIR / "errors.json"

    books_file.write_text(
        json.dumps(valid_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    errors_file.write_text(
        json.dumps(errors, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return valid_records, errors


def main():
    RUN_STATS["pages_fetched"] = 0
    RUN_STATS["cache_hits"] = 0
    RUN_STATS["failed_pages"] = []

    started_at = datetime.now(timezone.utc)
    start_time = perf_counter()

    book_urls = discover_catalogue_pages()

    fake_url = (
        "https://books.toscrape.com/catalogue/"
        "this-book-does-not-exist_99999/index.html"
    )
    book_urls.append(fake_url)

    raw_records = extract_all_raw_records(book_urls)
    valid_records, errors = validate_and_store_records(raw_records)

    duration_seconds = perf_counter() - start_time
    write_run_report(
        started_at=started_at,
        duration_seconds=duration_seconds,
        valid_records=valid_records,
        invalid_records=errors,
    )
    
    print("\n--- Run summary ---")
    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"failed_pages={len(RUN_STATS['failed_pages'])}")
    print(f"duration_seconds={duration_seconds:.2f}")
    print(f"report_file={OUTPUT_DIR / 'run-report.json'}")

if __name__ == "__main__":
    main()