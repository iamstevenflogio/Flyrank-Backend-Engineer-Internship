# The Polite Scraper

A Python scraping pipeline built for FlyRank Internship Week 5, Assignment A9. It collects the first three catalogue pages from Books to Scrape, extracts 60 book records, normalizes and validates them, caches responses, survives one intentionally broken URL, and writes an honest run report.

## Target classification

- **Target:** [Books to Scrape](https://books.toscrape.com/), a public practice sandbox for learning web scraping.
- **Why this target:** It is a fictional bookstore created specifically for safe scraping practice.
- **Scope:** This project processes only the first three catalogue pages and their 60 discovered book detail pages.
- **Robots check:** `https://books.toscrape.com/robots.txt` returned HTTP 404, so no robots file was found. A missing robots file is not permission by itself.
- **Why this is appropriate:** The target is a small public learning sandbox, the scope is deliberately limited, and the scraper uses caching and request delays.

I will not reuse this code on another site without checking its rules and terms first.

## Stack

- Python 3.10+
- `requests` for HTTP requests
- Beautiful Soup for HTML parsing
- Pydantic for schema validation

## Run locally

```powershell
git clone https://github.com/iamstevenflogio/Flyrank-Backend-Engineer-Internship.git
cd Flyrank-Backend-Engineer-Internship\Scraper-Python

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python src/main.py
```

The first run downloads the required pages and takes longer because it waits at least 0.5 seconds before each real request. Later runs read from `cache/` and are much faster.

## Output

A successful run writes:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

- `books.json`: 60 normalized, validated, unique book records.
- `errors.json`: validation failures with the reason and raw record.
- `run-report.json`: counts, duration, cache hits, fetches, and failed-page details.

## Record schema

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "Book description or null",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-08-28T00:00:00Z"
}
```

`product_url` is the canonical identity for each record. The scraper stores records in a dictionary keyed by that URL before writing `books.json`, so rerunning the script does not create duplicates.

## Politeness rules

- Sends an identifying `User-Agent` with a repository link.
- Uses a 10-second timeout for every real request.
- Waits at least 0.5 seconds before every real request.
- Caches downloaded catalogue and detail HTML in `cache/`; cached reads do not make network requests.
- Checks HTTP status codes before parsing.
- Retries once only after a timeout or server-side `5xx` response.
- Does not retry `403` or `404` responses.
- Handles one failed detail page independently so the remaining records still complete.

## Real run report

```json
{
  "started_at": "2026-08-27T16:20:57.448605Z",
  "duration_seconds": 13.91,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failures": [
    {
      "url": "https://books.toscrape.com/catalogue/this-book-does-not-exist_99999/index.html",
      "reason": "Fetch failed: status_code=404 url=https://books.toscrape.com/catalogue/this-book-does-not-exist_99999/index.html"
    }
  ]
}
```

## Why no browser?

This assignment did not need browser automation because the book data is already present in the HTML returned by the server. A browser would add startup time, memory usage, and complexity without improving the extraction.

## Limitation

This project intentionally handles only the first three catalogue pages. It also relies on the current Books to Scrape HTML structure, so selector updates would be needed if that page structure changes.

## Ethics

I would use an official API when one is available. I will not bypass logins, paywalls, robots restrictions, or access blocks, and I will collect only the minimum data needed for the project.
