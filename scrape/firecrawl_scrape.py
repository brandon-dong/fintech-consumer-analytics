"""
Scrapes the knowledge base source URLs using the Firecrawl API.
Writes one markdown file per URL to knowledge/raw/.
Skips files that already exist to make the script idempotent.

Usage:
    FIRECRAWL_API_KEY=<key> python scrape/firecrawl_scrape.py

Environment:
    FIRECRAWL_API_KEY  — Firecrawl API key (required)
"""

import os
import re
import sys
from datetime import date
from pathlib import Path

import requests

FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1/scrape"

SOURCES = [
    # CFPB — consumerfinance.gov
    ("https://www.consumerfinance.gov/about-us/", "cfpb_about_us.md"),
    ("https://www.consumerfinance.gov/about-us/the-bureau/", "cfpb_bureau_by_the_numbers.md"),
    ("https://www.consumerfinance.gov/data-research/consumer-complaints/", "cfpb_complaint_database_overview.md"),
    ("https://www.consumerfinance.gov/data-research/research-reports/supervisory-highlights/", "cfpb_supervisory_highlights.md"),
    ("https://www.consumerfinance.gov/data-research/research-reports/consumer-response-annual-report-2023/", "cfpb_consumer_response_annual_report_2023.md"),
    ("https://www.consumerfinance.gov/consumer-tools/prepaid-cards/", "cfpb_prepaid_cards_consumer_guide.md"),
    ("https://www.consumerfinance.gov/consumer-tools/money-as-you-grow/", "cfpb_money_as_you_grow.md"),
    ("https://www.consumerfinance.gov/about-us/newsroom/", "cfpb_newsroom_recent_enforcement.md"),
    # CFPB API docs — cfpb.github.io
    ("https://cfpb.github.io/api/ccdb/api.html", "cfpb_api_documentation.md"),
    # Greenlight — greenlight.com
    ("https://greenlight.com", "greenlight_homepage.md"),
    ("https://greenlight.com/how-it-works", "greenlight_how_it_works.md"),
    ("https://greenlight.com/safety", "greenlight_safety_infinity_features.md"),
    ("https://greenlight.com/learning-center", "greenlight_learning_center.md"),
    ("https://greenlight.com/learning-center/earning/average-allowance-by-age-for-kids", "greenlight_allowance_by_age.md"),
    ("https://greenlight.com/learning-center/family-safety/internet-safety", "greenlight_internet_safety_guide.md"),
]

OUTPUT_DIR = Path(__file__).parent.parent / "knowledge" / "raw"


def scrape_url(api_key: str, url: str) -> str:
    response = requests.post(
        FIRECRAWL_API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"url": url, "formats": ["markdown"]},
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise ValueError(f"Firecrawl returned success=false for {url}: {data}")
    return data["data"]["markdown"]


def build_header(url: str, filename: str) -> str:
    title = filename.replace(".md", "").replace("_", " ").title()
    today = date.today().isoformat()
    return f"# Source: {title}\n# URL: {url}\n# Scraped: {today}\n\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pending = [(url, fn) for url, fn in SOURCES if not (OUTPUT_DIR / fn).exists()]

    if not pending:
        print(f"All {len(SOURCES)} files already exist — nothing to scrape.")
        return

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("ERROR: FIRECRAWL_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    scraped = 0
    errors = 0

    for url, filename in pending:
        out_path = OUTPUT_DIR / filename
        print(f"  fetch {url} → {filename}")
        try:
            markdown = scrape_url(api_key, url)
            header = build_header(url, filename)
            out_path.write_text(header + markdown, encoding="utf-8")
            print(f"  wrote {filename} ({len(markdown):,} chars)")
            scraped += 1
        except Exception as exc:
            print(f"  ERROR scraping {url}: {exc}", file=sys.stderr)
            errors += 1

    skipped = len(SOURCES) - len(pending)
    print(f"\nDone: {scraped} scraped, {skipped} skipped, {errors} errors")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
