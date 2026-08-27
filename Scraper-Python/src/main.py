from pathlib import Path
import requests

PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (https://github.com/iamstevenflogio/Flyrank-Backend-Engineer-Internship)"
TIMEOUT_SECONDS = 10

def fetch_and_cache(url: str, cache_file: Path) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT size_bytes={len(html.encode('utf-8'))}")
        return html

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)

    if response.status_code != 200:
        raise RuntimeError(f"Fetch failed with status code {response.status_code} for {url}")

    html = response.text
    cache_file.write_text(html, encoding="utf-8")
    print(f"FETCH size_bytes={len(html.encode('utf-8'))}")
    return html

def main():
    fetch_and_cache(PAGE_URL, CACHE_FILE)

if __name__ == "__main__":
    main()