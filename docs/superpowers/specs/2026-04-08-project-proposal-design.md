# Project Proposal Design: Fintech Consumer Analytics
**Date:** 2026-04-08
**Job Posting:** Associate Data Analyst, Greenlight Financial Technology (Atlanta, GA — Remote Friendly)
**Repo Name:** `fintech-consumer-analytics`
**Proposal Due:** April 13, 2026 at 9:55 AM

---

## 1. Overview

Build an end-to-end analytics pipeline on the **CFPB Consumer Complaint Database** to analyze complaint trends across fintech products and companies. The project mirrors the core work of a Marketing Science analyst at Greenlight: understanding consumer trust signals, identifying quality gaps in competitor products, and surfacing actionable KPIs through a dashboard.

**Central business question:** Which fintech products and companies are losing consumer trust, and why?

- **Descriptive layer:** What products/companies generate the most complaints? Where are they concentrated geographically?
- **Diagnostic layer:** Why are consumers disputing resolutions? Which company behaviors correlate with high dispute rates?

**Transferability:** This project transfers to any consumer fintech, banking, regtech, or CRM analytics role — any employer who cares about customer satisfaction, competitive intelligence, or regulatory risk.

---

## 2. Architecture & Data Flow

```
CFPB REST API
    │
    ▼
Python extraction script (cfpb_extract.py)
    │  pulls complaints filtered by product category
    │  (Checking/savings, Credit card, Money transfer, Mortgage)
    ▼
GitHub Actions (scheduled daily)
    │
    ▼
Snowflake RAW schema
    └── RAW.CFPB_COMPLAINTS (raw JSON/CSV, append-only)
    │
    ▼
dbt Staging Layer  (stg_cfpb_complaints.sql)
    │  clean, rename, type cast, deduplicate
    ▼
dbt Mart Layer  (star schema)
    ├── fact_complaints
    ├── dim_product
    ├── dim_company
    ├── dim_issue
    ├── dim_geography
    └── dim_date
    │
    ▼
Streamlit Dashboard (deployed → Streamlit Community Cloud)
    └── Connected to Snowflake mart tables via st.connection("snowflake")

Web Scrape Path (separate GitHub Actions job):
    CFPB reports + fintech blogs + Greenlight press → knowledge/raw/
    Claude Code → knowledge/wiki/ (synthesized insights)
```

**Key architectural decisions:**
- Raw layer is append-only — source data is never overwritten
- Staging handles all cleaning so mart models stay clean and reusable
- GitHub Actions runs on a schedule (daily at 6 AM UTC)
- CFPB API supports filtering by product, date range, and company
- All credentials stored as GitHub Secrets / environment variables; nothing committed to repo

---

## 3. Star Schema Design

### fact_complaints
| Column | Type | Notes |
|---|---|---|
| complaint_key | INT (PK) | surrogate key |
| product_key | INT (FK) | → dim_product |
| company_key | INT (FK) | → dim_company |
| issue_key | INT (FK) | → dim_issue |
| geography_key | INT (FK) | → dim_geography |
| date_key | INT (FK) | → dim_date |
| complaint_id | VARCHAR | CFPB natural key |
| submitted_via | VARCHAR | web, phone, referral, fax |
| timely_response_flag | BOOLEAN | company responded on time |
| consumer_disputed_flag | BOOLEAN | consumer disputed resolution |
| consumer_consent_provided | VARCHAR | consent level for narrative |

### dim_product
| Column | Type |
|---|---|
| product_key | INT (PK) |
| product_name | VARCHAR |
| product_category | VARCHAR |

### dim_company
| Column | Type |
|---|---|
| company_key | INT (PK) |
| company_name | VARCHAR |
| company_response | VARCHAR |

### dim_issue
| Column | Type |
|---|---|
| issue_key | INT (PK) |
| issue | VARCHAR |
| sub_issue | VARCHAR |

### dim_geography
| Column | Type |
|---|---|
| geography_key | INT (PK) |
| state | VARCHAR |
| zip_code | VARCHAR |

### dim_date
| Column | Type |
|---|---|
| date_key | INT (PK) |
| full_date | DATE |
| year | INT |
| quarter | INT |
| month | INT |
| month_name | VARCHAR |
| week_of_year | INT |

**Analytic questions this schema answers:**
- Which product categories generate the most complaints? (descriptive)
- Which companies have the highest dispute rates? (diagnostic)
- Are complaint volumes trending up or down for mobile banking? (trend)
- What specific issues drive the most consumer disputes? (root cause)

---

## 4. Streamlit Dashboard

### View 1 — Descriptive: "What's happening in fintech complaints?"
- KPI cards: Total complaints, % timely response, % consumer disputed, avg complaints/month
- Line chart: Complaint volume over time, filterable by product category
- Bar chart: Top 10 companies by complaint volume
- Choropleth map: Complaint density by state
- *Takeaway title:* "Mobile banking complaints have grown 34% YoY while dispute rates remain highest for prepaid cards"

### View 2 — Diagnostic: "Why are consumers disputing resolutions?"
- Scatter plot: Company complaint volume vs. dispute rate (outlier identification)
- Stacked bar: Issue breakdown by product category
- Funnel: Company response outcomes (closed with relief → closed without relief → untimely)
- *Takeaway title:* "Companies that close complaints 'without relief' are 3x more likely to receive a consumer dispute"

### Interactive Elements
- Date range slider (affects all charts)
- Product category multi-select filter
- Company search/filter on diagnostic view

**Deployment:** Streamlit Community Cloud, `st.connection("snowflake")`, secrets via Streamlit secrets management.

---

## 5. Knowledge Base

### Scrape Targets (15+ raw sources from 3+ sites/authors)
| Source | Type | Target Count |
|---|---|---|
| CFPB annual reports + research papers | PDF/web | 4-5 |
| Greenlight blog, press releases, about pages | Web | 3-4 |
| Fintech competitor sites (Step, Current, Copper) | Web | 3-4 |
| Industry analysis (Forbes Fintech, TechCrunch) | Web | 3-4 |
| Youth financial literacy orgs (NEFE, Jump$tart) | Web | 2-3 |

All saved to `knowledge/raw/` as markdown or text files, automated via GitHub Actions.

### Wiki Pages (`knowledge/wiki/`)
- `overview.md` — Consumer fintech complaint landscape: key players, regulatory context, market size
- `key-entities.md` — Greenlight, CFPB, competitors, product categories defined
- `complaint-themes.md` — Synthesized patterns: issues that recur across companies and products
- `index.md` — One-line summaries of all wiki pages, queryable entry point

### CLAUDE.md Knowledge Base Section
Instructs Claude Code: "When asked about the fintech knowledge base, read `knowledge/index.md` first, then pull from relevant wiki pages and raw sources to answer."

### Final Interview Demo Script
> "What does my knowledge base say about why mobile banking apps generate consumer disputes?"

---

## 6. Repo Structure

```
fintech-consumer-analytics/
├── .github/
│   └── workflows/
│       ├── extract_cfpb.yml         # scheduled API extraction
│       └── scrape_knowledge.yml     # knowledge base scraping
├── docs/
│   ├── job-posting.pdf
│   ├── proposal.pdf
│   └── superpowers/specs/           # design docs
├── extract/
│   └── cfpb_extract.py              # CFPB API extraction script
├── transform/
│   └── dbt_project/                 # dbt models
│       ├── models/staging/
│       └── models/mart/
├── dashboard/
│   └── app.py                       # Streamlit app
├── knowledge/
│   ├── raw/                         # scraped sources
│   └── wiki/                        # Claude Code-generated wiki
├── .gitignore
├── CLAUDE.md
└── README.md
```

---

## 7. Proposal & README Files

Actual deliverable files created and committed:

- **`docs/proposal.md`** — follows `proposal-template.md` exactly. Includes name, project name, repo link placeholder, job posting details, SQL requirement quote (two quotes from the posting), and a reflection paragraph that answers all 4 required questions: relevance to class, specific coursework skills, what you'd build, and 2-3 transferable roles.
- **`README.md`** — follows `readme-template.md` exactly. All Milestone 02 sections (pipeline diagram, ERD, dashboard screenshot, live URL, key insights) are marked with `<!-- Coming in Milestone 01/02 -->` placeholders so the structure is in place and graders can see the intent.

**Reflection paragraph (in `docs/proposal.md`):**

This posting is directly relevant to ISBA 4715 because it requires the exact skills this course covers: SQL for ad-hoc analysis and user list generation, dbt for building and maintaining attribution pipelines with scalable data models, dashboards for surfacing KPIs to marketing and leadership stakeholders, Python for data extraction and automation, and AI proficiency with Claude — which the posting explicitly calls out as a first-class tool on the team. To prove I can do this job, I am building an end-to-end analytics pipeline on the CFPB Consumer Complaint Database: extracting complaint data via REST API, loading it to Snowflake, modeling it into a star schema through dbt staging and mart layers, and surfacing complaint trends and dispute rates through a deployed Streamlit dashboard — the same workflow a Marketing Science analyst at Greenlight would use to understand consumer trust signals across their competitive landscape. Beyond Greenlight, this project transfers directly to data analyst roles at any consumer fintech company (Chime, SoFi, Wise), to regtech and compliance analytics roles where CFPB data is a primary source, and to CRM analytics roles where dispute rates and resolution quality are core customer satisfaction KPIs.

---

## 8. Milestone Map

| Milestone | Due | Key Work |
|---|---|---|
| Proposal | Apr 13 | Job posting PDF, proposal PDF, repo initialized with CLAUDE.md |
| Milestone 01 | Apr 27 | CFPB extraction + Snowflake load, dbt staging + mart, GitHub Actions, pipeline diagram |
| Milestone 02 | May 4 | Knowledge base scraping, Streamlit dashboard deployed, slides, README, ERD |
| Final Submission | May 11 | Updated resume committed to repo |

---

## 9. Transferability

Beyond Greenlight, this project transfers to:
- **Any consumer fintech** (Chime, SoFi, Robinhood, Wise) — complaint/trust analytics is universal
- **Regtech / compliance analytics** — CFPB data is the core data source for regulatory analysts
- **CRM analytics roles** — dispute rate and response quality are CRM KPIs by another name
- **Growth/marketing analytics** — complaint velocity as a leading indicator of churn
