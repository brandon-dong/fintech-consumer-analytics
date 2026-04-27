# Source: CFPB Consumer Complaint Database API Documentation
# URL: https://cfpb.github.io/api/ccdb/api.html
# Scraped: 2026-04-27

## Consumer Complaint Database API (v1.0.0 / OAS3)

Base URL: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/

License: Creative Commons CC0 (Public Domain)

## Endpoints

### Complaints
- `GET /` — Search consumer complaints (used in this project's extraction script)
- `GET /{complaintId}` — Find consumer complaint by ID
- `GET /geo/states` — Get state-by-state aggregated information

### Trends
- `GET /trends` — List aggregated complaint trends over time

### Typeahead (autocomplete support)
- `GET /_suggest` — Suggest possible search terms
- `GET /_suggest_company` — Suggest possible company names
- `GET /_suggest_zip` — Suggest possible zip codes

## Key Data Schemas

- **Complaint** — individual complaint record with fields: complaint_id, date_received, product, sub_product, issue, sub_issue, company, state, zip_code, submitted_via, company_response, timely, consumer_disputed, consumer_consent_provided
- **SearchResult** — paginated search response containing Hits and Meta
- **Hits** — array of Hit objects (each Hit contains a `_source` Complaint)
- **TrendsResult** — aggregated complaint counts over time buckets
- **StatesResult** — geographic complaint distribution by state

## API Usage in This Project

The `extract/cfpb_extract.py` script calls `GET /` with parameters:
- `date_received_min` / `date_received_max` — date range filter
- `product` — one of 4 fintech product categories
- `format=json` — returns flat list of `{_source: Complaint}` objects

The API returns a flat list (NOT Elasticsearch-style `hits.hits` nesting), which the extract script handles by iterating directly over the response and accessing `h["_source"]` for each item.

## Relevance

This API is the direct data source for our entire pipeline. Understanding the schema enables proper field mapping between API response → RAW table → staging → mart.
