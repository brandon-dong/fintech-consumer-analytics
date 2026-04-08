# CLAUDE.md — Fintech Consumer Analytics

## Project Overview

End-to-end analytics pipeline on the CFPB Consumer Complaint Database.
Analyzes complaint trends across fintech products and companies to surface
consumer trust signals. Built to demonstrate Marketing Science analyst skills
targeting the Greenlight Financial Technology Associate Data Analyst role.

**Central business question:** Which fintech products and companies are losing
consumer trust, and why?

## Tech Stack

- **Extraction:** Python (cfpb_extract.py) via CFPB REST API
- **Data Warehouse:** Snowflake (AWS US East 1)
- **Transformation:** dbt Core
- **Orchestration:** GitHub Actions (scheduled daily, 6 AM UTC)
- **Dashboard:** Streamlit (deployed to Streamlit Community Cloud)
- **Knowledge Base:** Claude Code (scrape → summarize → query)

## Snowflake Schema Structure

```
Database: FINTECH_ANALYTICS
├── RAW           ← append-only raw loads, never modified after insert
│   └── CFPB_COMPLAINTS
├── STAGING       ← dbt staging models (clean, renamed, type-cast)
│   └── STG_CFPB_COMPLAINTS
└── MART          ← dbt mart models (star schema)
    ├── FACT_COMPLAINTS
    ├── DIM_PRODUCT
    ├── DIM_COMPANY
    ├── DIM_ISSUE
    ├── DIM_GEOGRAPHY
    └── DIM_DATE
```

## Directory Structure

```
fintech-consumer-analytics/
├── .github/workflows/
│   ├── extract_cfpb.yml       # daily CFPB extraction to Snowflake
│   └── scrape_knowledge.yml   # knowledge base scraping
├── extract/
│   └── cfpb_extract.py        # CFPB API → Snowflake RAW
├── dbt_project/
│   ├── models/
│   │   ├── staging/           # stg_cfpb_complaints.sql
│   │   └── mart/              # fact_complaints.sql, dim_*.sql
│   ├── tests/                 # dbt schema tests
│   └── dbt_project.yml
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── knowledge/
│   ├── raw/                   # scraped sources (15+ files)
│   └── wiki/                  # Claude Code-generated wiki pages
│       ├── index.md
│       ├── overview.md
│       ├── key-entities.md
│       └── complaint-themes.md
├── docs/
│   ├── job-posting.pdf
│   ├── proposal.pdf
│   └── superpowers/
│       ├── specs/             # design documents
│       └── plans/             # implementation plans
├── .env.example
├── .gitignore
├── CLAUDE.md                  # this file
└── README.md
```

## Environment Variables

All credentials are in `.env` (gitignored). Copy `.env.example` to `.env`.
GitHub Actions uses repository secrets with the same variable names.

Never commit `.env`, `profiles.yml`, or any file containing credentials.

## dbt Conventions

- Staging models: `stg_<source>_<entity>.sql` — one model per source table
- Mart models: `fact_<entity>.sql`, `dim_<entity>.sql`
- All mart models materialized as `table` in Snowflake
- At least one schema test per model (not_null on PKs, unique on natural keys)
- Run with: `cd dbt_project && dbt run && dbt test`

## Knowledge Base — Query Conventions

When asked to answer questions about the fintech knowledge base:

1. Read `knowledge/index.md` first to understand what's available
2. Read the relevant wiki page(s) in `knowledge/wiki/`
3. Fall back to specific files in `knowledge/raw/` for source-level detail
4. Synthesize across sources — do not just summarize one file
5. Cite your sources (filename) when making specific claims

**Example queries:**
- "What does my knowledge base say about why mobile banking apps generate consumer disputes?"
- "Which fintech companies have the worst complaint resolution track record?"
- "What regulatory trends from CFPB reports should a family fintech company watch?"

## Star Schema — Key Fields

`fact_complaints` analytic measures:
- `timely_response_flag` — did the company respond on time? (Boolean)
- `consumer_disputed_flag` — did the consumer dispute the resolution? (Boolean)
- `submitted_via` — channel (web, phone, referral, fax)

These three fields are the core of all dashboard analytics. High `consumer_disputed_flag`
rate = poor company response quality. Low `timely_response_flag` rate = operational issues.
