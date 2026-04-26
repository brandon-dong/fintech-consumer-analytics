"""CFPB Consumer Complaint API extractor → Snowflake RAW.CFPB_COMPLAINTS."""

import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CFPB_API_URL = (
    "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
)
PRODUCTS = [
    "Checking or savings account",
    "Credit card or prepaid card",
    "Money transfer, virtual currency, or money service",
    "Mortgage",
]
BACKFILL_START = "2023-01-01"
PAGE_SIZE = 10_000


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ.get("SNOWFLAKE_DATABASE", "FINTECH_ANALYTICS"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        schema="RAW",
    )


def ensure_table(conn) -> None:
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS FINTECH_ANALYTICS.RAW.CFPB_COMPLAINTS (
            complaint_id                 VARCHAR,
            date_received                VARCHAR,
            product                      VARCHAR,
            sub_product                  VARCHAR,
            issue                        VARCHAR,
            sub_issue                    VARCHAR,
            company                      VARCHAR,
            state                        VARCHAR,
            zip_code                     VARCHAR,
            submitted_via                VARCHAR,
            date_sent_to_company         VARCHAR,
            company_response_to_consumer VARCHAR,
            timely_response              VARCHAR,
            consumer_disputed            VARCHAR,
            consumer_consent_provided    VARCHAR,
            loaded_at                    TIMESTAMP
        )
    """)


def get_max_date(conn) -> Optional[str]:
    """Return MAX(date_received) from RAW, or None if the table is empty."""
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(date_received) FROM FINTECH_ANALYTICS.RAW.CFPB_COMPLAINTS"
    )
    result = cur.fetchone()[0]
    return str(result) if result else None


def get_existing_ids(conn, date_from: str) -> set:
    cur = conn.cursor()
    cur.execute(
        "SELECT complaint_id FROM FINTECH_ANALYTICS.RAW.CFPB_COMPLAINTS "
        "WHERE date_received >= %s",
        (date_from,)
    )
    return {row[0] for row in cur.fetchall()}


def fetch_complaints(date_from: str, date_to: str) -> list:
    """Fetch all complaints across all target products for the given date range."""
    all_complaints = []
    for product in PRODUCTS:
        log.info("Fetching product: %s", product)
        params = {
            "date_received_min": date_from,
            "date_received_max": date_to,
            "product": product,
            "format": "json",
        }
        resp = requests.get(CFPB_API_URL, params=params, timeout=120)
        resp.raise_for_status()
        hits = resp.json()
        all_complaints.extend(h["_source"] for h in hits)
        log.info("  Got %d complaints", len(hits))
    return all_complaints


def parse_complaint(raw: dict) -> tuple:
    """Map a CFPB API _source dict to an ordered tuple matching RAW table columns."""
    return (
        raw.get("complaint_id"),
        raw.get("date_received"),
        raw.get("product"),
        raw.get("sub_product"),
        raw.get("issue"),
        raw.get("sub_issue"),
        raw.get("company"),
        raw.get("state"),
        raw.get("zip_code"),
        raw.get("submitted_via"),
        raw.get("date_sent_to_company"),
        raw.get("company_response"),
        raw.get("timely"),
        raw.get("consumer_disputed"),
        raw.get("consumer_consent_provided"),
        datetime.now(timezone.utc).isoformat(),
    )


def load_to_snowflake(conn, rows: list) -> None:
    if not rows:
        log.info("No new rows to insert.")
        return
    sql = """
        INSERT INTO FINTECH_ANALYTICS.RAW.CFPB_COMPLAINTS (
            complaint_id, date_received, product, sub_product, issue, sub_issue,
            company, state, zip_code, submitted_via, date_sent_to_company,
            company_response_to_consumer, timely_response, consumer_disputed,
            consumer_consent_provided, loaded_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    conn.cursor().executemany(sql, rows)
    log.info("Inserted %d rows.", len(rows))


def main():
    conn = get_snowflake_connection()
    ensure_table(conn)

    max_date = get_max_date(conn)
    if max_date is None:
        date_from = BACKFILL_START
        log.info("Empty table — running full backfill from %s.", date_from)
    else:
        date_from = str(date.fromisoformat(max_date) + timedelta(days=1))
        log.info("Incremental load from %s.", date_from)

    date_to = str(date.today())
    log.info("Date range: %s → %s", date_from, date_to)

    raw_complaints = fetch_complaints(date_from, date_to)
    log.info("Fetched %d total complaints from API.", len(raw_complaints))

    existing_ids = get_existing_ids(conn, date_from)
    new_rows = [
        parse_complaint(c)
        for c in raw_complaints
        if c.get("complaint_id") not in existing_ids
    ]
    log.info("%d new complaints after deduplication.", len(new_rows))

    load_to_snowflake(conn, new_rows)
    conn.close()
    log.info("Done.")


if __name__ == "__main__":
    main()
