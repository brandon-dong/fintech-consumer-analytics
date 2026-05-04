# Dashboard Design — Fintech Consumer Analytics
**Date:** 2026-05-03
**Milestone:** 02 (due 2026-05-04 at 9:55 AM)

---

## Overview

A single-file Streamlit dashboard (`dashboard/app.py`) connected to the Snowflake mart layer. Answers two business questions:

- **Descriptive:** Which fintech products and companies generate the most consumer complaints, and how has volume changed over time?
- **Diagnostic:** Why are consumers dissatisfied — and which companies are failing to resolve complaints?

---

## Architecture

**File structure:**
```
dashboard/
└── app.py
.streamlit/
└── secrets.toml        # gitignored — Snowflake creds for local dev
requirements.txt        # repo root: streamlit, snowflake-connector-python, pandas, plotly
```

**Snowflake connection:** `st.connection("snowflake")` using Streamlit's built-in Snowflake connector. Credentials sourced from `.streamlit/secrets.toml` locally and Streamlit Community Cloud's Secrets UI for production.

**Querying pattern:** SQL strings defined as constants at the top of `app.py`. Sidebar filter values passed as parameterized inputs to avoid injection. Filter option lists loaded once on startup with `@st.cache_data(ttl=3600)`.

**Secrets format (`.streamlit/secrets.toml`):**
```toml
[connections.snowflake]
account   = "..."
user      = "..."
password  = "..."
database  = "FINTECH_ANALYTICS"
warehouse = "basket_craft_wh"
role      = ""
```

---

## Sidebar Filters (global — both tabs)

| Filter | Widget | Source | Default |
|---|---|---|---|
| Product | `st.multiselect` | `dim_product.product_name` | All selected |
| Year | `st.multiselect` | `dim_date.year` (distinct) | All selected |

Both filter option lists are cached for 1 hour. Selected values are injected into all tab queries via SQL `IN` clauses.

---

## Tab 1: "📊 Complaint Trends" (Descriptive)

Answers: **What happened?**

### Chart 1 — Monthly Complaint Volume
- **Type:** Line chart (Plotly)
- **X:** `year-month` string (e.g., `"2024-03"`)
- **Y:** complaint count
- **Query:** `fact_complaints` joined to `dim_date`, grouped by year + month, filtered by sidebar selections
- **Takeaway title:** dynamically states peak month and volume

### Chart 2 — Complaints by Product
- **Type:** Horizontal bar chart (Plotly)
- **X:** complaint count | **Y:** product name (top 10)
- **Query:** `fact_complaints` joined to `dim_product`, grouped by `product_name`, filtered by sidebar
- **Takeaway title:** names the #1 product by volume

### Chart 3 — Submission Channel Breakdown
- **Type:** Horizontal bar chart (Plotly)
- **X:** complaint count | **Y:** `submitted_via` value
- **Query:** `fact_complaints`, grouped by `submitted_via`, filtered by sidebar
- **Takeaway title:** states web % of total (relevant to Greenlight's mobile-native audience)

---

## Tab 2: "🔍 Resolution Quality" (Diagnostic)

Answers: **Why are consumers dissatisfied?**

### Chart 4 — Dispute Rate by Product
- **Type:** Horizontal bar chart (Plotly), sorted descending
- **X:** dispute rate (%) | **Y:** product name
- **Query:** `fact_complaints` joined to `dim_product`, `consumer_disputed_flag = true` count / total count per product
- **Takeaway title:** names the highest-dispute-rate product

### Chart 5 — Timely Response Rate by Product
- **Type:** Horizontal bar chart (Plotly), sorted ascending (worst first)
- **X:** timely response rate (%) | **Y:** product name
- **Query:** `fact_complaints` joined to `dim_product`, `timely_response_flag = true` count / total count per product
- **Takeaway title:** highlights the product with lowest timely response rate

### Company Drill-Down
- **Widget:** `st.selectbox` — company name, defaults to "Greenlight"
- **Output:** Three `st.metric` cards (dispute rate %, timely response rate %, total complaints) + a table of top 5 complaint issues
- **Query:** `fact_complaints` joined to `dim_company` and `dim_issue`, filtered to selected company
- **Takeaway title:** compares selected company's dispute rate to the dataset average (dynamically computed)

---

## Deployment

**Platform:** Streamlit Community Cloud (`share.streamlit.io`)

**Steps:**
1. Connect GitHub repo at `share.streamlit.io`
2. Set main file path to `dashboard/app.py`
3. Paste Snowflake credentials into the Secrets panel (matching `.streamlit/secrets.toml` format)
4. Deploy — public URL auto-generated

Dashboard redeploys automatically on every push to `main`.

---

## Rubric Coverage

| Requirement | Met by |
|---|---|
| Connected to Snowflake mart tables | `st.connection("snowflake")` against `FINTECH_ANALYTICS.MART` |
| Descriptive analytics view | Tab 1 — Complaint Trends (3 charts) |
| Diagnostic analytics view | Tab 2 — Resolution Quality (2 charts + drill-down) |
| Interactive element | Tabs + sidebar filters + company selectbox |
| Deployed with public URL | Streamlit Community Cloud |
