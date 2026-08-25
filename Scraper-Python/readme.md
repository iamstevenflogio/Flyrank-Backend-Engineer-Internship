# The Polite Scraper

A Python web-scraping pipeline for FlyRank Internship Week 5, Assignment A9.

## Target classification

- **Target:** [Books to Scrape](https://books.toscrape.com/), a public practice sandbox created for people learning web scraping.
- **Why this target:** Books to Scrape is intentionally designed for scraping practice, making it appropriate for this assignment.
- **Scope:** This project will scrape only the first 3 catalogue pages and discover their 60 book detail pages.
- **Data collected:** Each book record will include the title, product URL, price text, availability text, rating text, description, source catalogue page, and fetch timestamp.
- **Robots check:** I requested `https://books.toscrape.com/robots.txt` once and received a 404 response: **no robots file found**. A missing robots file is not permission; it is only a missing file.
- **Why this is appropriate:** This is a limited scrape of a public sandbox made for practice, rather than a real commercial or private website.

I will not reuse this code on another site without checking its rules and terms first.
