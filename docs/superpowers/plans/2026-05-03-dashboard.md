# Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a two-tab Streamlit dashboard connected to the Snowflake mart layer that answers what happened (descriptive) and why consumers are dissatisfied (diagnostic).

**Architecture:** Single-page app (`dashboard/app.py`) using `st.connection("snowflake")`. Pure helper functions live in `dashboard/helpers.py` for testability. All SQL is defined as module-level string constants; sidebar filter values are injected via safe string formatting (values sourced from the DB, not raw user input). Cached with `@st.cache_data`.

**Tech Stack:** Python 3.11, Streamlit ≥1.32, snowflake-connector-python[pandas] ≥3.10, Plotly ≥5.0, pandas ≥2.0, pytest

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `requirements.txt` | Create | Root-level deps for Streamlit Community Cloud |
| `dashboard/helpers.py` | Create | Pure helper functions: `str_in_clause`, `int_in_clause` |
| `dashboard/app.py` | Create | Full Streamlit UI — page config, connection, SQL, sidebar, tabs |
| `tests/test_helpers.py` | Create | Unit tests for helpers |
| `.streamlit/secrets.toml` | Create locally (never commit) | Snowflake creds for local dev |

---

## Task 1: Requirements and secrets scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.streamlit/secrets.toml` (local only — already gitignored)

- [ ] **Step 1: Create root `requirements.txt`**

```
streamlit>=1.32.0
snowflake-connector-python[pandas]>=3.10.0
pandas>=2.0.0
plotly>=5.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create `.streamlit/secrets.toml` with your real credentials**

```toml
[connections.snowflake]
account   = "<your-account-locator>"
user      = "<your-username>"
password  = "<your-password>"
database  = "FINTECH_ANALYTICS"
warehouse = "basket_craft_wh"
role      = ""
```

> The `account` value is the locator from your Snowflake URL, e.g. `xy12345.us-east-1`.
> `.streamlit/` is already in `.gitignore` — this file will never be committed.

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "feat(dashboard): add root requirements.txt for Streamlit Community Cloud"
```

---

## Task 2: Helper functions (TDD)

**Files:**
- Create: `dashboard/helpers.py`
- Create: `tests/test_helpers.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_helpers.py`:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from dashboard.helpers import str_in_clause, int_in_clause


def test_str_in_clause_multiple():
    assert str_in_clause(["Credit card", "Checking"]) == "('Credit card', 'Checking')"


def test_str_in_clause_single():
    assert str_in_clause(["Prepaid card"]) == "('Prepaid card')"


def test_str_in_clause_escapes_single_quotes():
    assert str_in_clause(["it's"]) == "('it''s')"


def test_int_in_clause_multiple():
    assert int_in_clause([2023, 2024]) == "(2023, 2024)"


def test_int_in_clause_single():
    assert int_in_clause([2024]) == "(2024)"
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_helpers.py -v
```

Expected: `ModuleNotFoundError: No module named 'dashboard'`

- [ ] **Step 3: Create `dashboard/__init__.py` (empty) and `dashboard/helpers.py`**

Create `dashboard/__init__.py` as an empty file.

Create `dashboard/helpers.py`:

```python
def str_in_clause(values: list) -> str:
    escaped = [str(v).replace("'", "''") for v in values]
    return "('" + "', '".join(escaped) + "')"


def int_in_clause(values: list) -> str:
    return "(" + ", ".join(str(int(v)) for v in values) + ")"
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_helpers.py -v
```

Expected:
```
PASSED tests/test_helpers.py::test_str_in_clause_multiple
PASSED tests/test_helpers.py::test_str_in_clause_single
PASSED tests/test_helpers.py::test_str_in_clause_escapes_single_quotes
PASSED tests/test_helpers.py::test_int_in_clause_multiple
PASSED tests/test_helpers.py::test_int_in_clause_single
5 passed
```

- [ ] **Step 5: Commit**

```bash
git add dashboard/__init__.py dashboard/helpers.py tests/test_helpers.py
git commit -m "feat(dashboard): add SQL IN-clause helpers with tests"
```

---

## Task 3: App skeleton — connection, SQL constants, sidebar

**Files:**
- Create: `dashboard/app.py`

- [ ] **Step 1: Create `dashboard/app.py` with page config, connection, and all SQL constants**

```python
import streamlit as st
import plotly.express as px

from dashboard.helpers import str_in_clause, int_in_clause

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fintech Consumer Analytics",
    page_icon="📊",
    layout="wide",
)

# ── Snowflake connection ──────────────────────────────────────────────────────
conn = st.connection("snowflake")

# ── SQL constants ─────────────────────────────────────────────────────────────
_MART = "FINTECH_ANALYTICS.MART"

SQL_PRODUCTS = f"SELECT DISTINCT product_name FROM {_MART}.DIM_PRODUCT ORDER BY 1"
SQL_YEARS    = f"SELECT DISTINCT year FROM {_MART}.DIM_DATE ORDER BY 1"
SQL_COMPANIES = f"SELECT DISTINCT company_name FROM {_MART}.DIM_COMPANY ORDER BY 1"

SQL_MONTHLY_VOLUME = f"""
    SELECT dd.year || '-' || LPAD(dd.month::VARCHAR, 2, '0') AS year_month,
           COUNT(*) AS complaint_count
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_DATE dd    ON f.date_key    = dd.date_key
    JOIN {_MART}.DIM_PRODUCT dp ON f.product_key = dp.product_key
    WHERE dp.product_name IN {{products}}
      AND dd.year IN {{years}}
    GROUP BY 1 ORDER BY 1
"""

SQL_BY_PRODUCT = f"""
    SELECT dp.product_name, COUNT(*) AS complaint_count
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_PRODUCT dp ON f.product_key = dp.product_key
    JOIN {_MART}.DIM_DATE dd    ON f.date_key    = dd.date_key
    WHERE dp.product_name IN {{products}}
      AND dd.year IN {{years}}
    GROUP BY 1 ORDER BY 2 DESC LIMIT 10
"""

SQL_CHANNELS = f"""
    SELECT COALESCE(f.submitted_via, 'unknown') AS channel,
           COUNT(*) AS complaint_count
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_DATE dd    ON f.date_key    = dd.date_key
    JOIN {_MART}.DIM_PRODUCT dp ON f.product_key = dp.product_key
    WHERE dp.product_name IN {{products}}
      AND dd.year IN {{years}}
    GROUP BY 1 ORDER BY 2 DESC
"""

SQL_DISPUTE_RATE = f"""
    SELECT dp.product_name,
           ROUND(100.0 * SUM(CASE WHEN f.consumer_disputed_flag = TRUE THEN 1 ELSE 0 END)
                 / NULLIF(SUM(CASE WHEN f.consumer_disputed_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
               AS dispute_rate_pct
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_PRODUCT dp ON f.product_key = dp.product_key
    JOIN {_MART}.DIM_DATE dd    ON f.date_key    = dd.date_key
    WHERE dp.product_name IN {{products}}
      AND dd.year IN {{years}}
    GROUP BY 1 HAVING COUNT(*) >= 50
    ORDER BY 2 DESC
"""

SQL_TIMELY_RATE = f"""
    SELECT dp.product_name,
           ROUND(100.0 * SUM(CASE WHEN f.timely_response_flag = TRUE THEN 1 ELSE 0 END)
                 / NULLIF(SUM(CASE WHEN f.timely_response_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
               AS timely_rate_pct
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_PRODUCT dp ON f.product_key = dp.product_key
    JOIN {_MART}.DIM_DATE dd    ON f.date_key    = dd.date_key
    WHERE dp.product_name IN {{products}}
      AND dd.year IN {{years}}
    GROUP BY 1 HAVING COUNT(*) >= 50
    ORDER BY 2 ASC
"""

SQL_COMPANY_METRICS = f"""
    SELECT COUNT(*) AS total_complaints,
           ROUND(100.0 * SUM(CASE WHEN f.consumer_disputed_flag = TRUE THEN 1 ELSE 0 END)
                 / NULLIF(SUM(CASE WHEN f.consumer_disputed_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
               AS dispute_rate_pct,
           ROUND(100.0 * SUM(CASE WHEN f.timely_response_flag = TRUE THEN 1 ELSE 0 END)
                 / NULLIF(SUM(CASE WHEN f.timely_response_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
               AS timely_rate_pct
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_COMPANY dc ON f.company_key = dc.company_key
    WHERE dc.company_name = '{{company}}'
"""

SQL_COMPANY_ISSUES = f"""
    SELECT di.issue, COUNT(*) AS complaint_count
    FROM {_MART}.FACT_COMPLAINTS f
    JOIN {_MART}.DIM_COMPANY dc ON f.company_key = dc.company_key
    JOIN {_MART}.DIM_ISSUE di   ON f.issue_key   = di.issue_key
    WHERE dc.company_name = '{{company}}'
    GROUP BY 1 ORDER BY 2 DESC LIMIT 5
"""

SQL_AVG_DISPUTE = f"""
    SELECT ROUND(100.0 * SUM(CASE WHEN consumer_disputed_flag = TRUE THEN 1 ELSE 0 END)
           / NULLIF(SUM(CASE WHEN consumer_disputed_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
           AS avg_dispute_rate
    FROM {_MART}.FACT_COMPLAINTS
"""
```

- [ ] **Step 2: Add cached data-loading functions below the SQL constants**

Append to `dashboard/app.py`:

```python
# ── Cached loaders ────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_products():
    return conn.query(SQL_PRODUCTS, ttl=0)["PRODUCT_NAME"].tolist()


@st.cache_data(ttl=3600)
def load_years():
    return sorted(conn.query(SQL_YEARS, ttl=0)["YEAR"].tolist())


@st.cache_data(ttl=3600)
def load_companies():
    return conn.query(SQL_COMPANIES, ttl=0)["COMPANY_NAME"].tolist()


@st.cache_data(ttl=600)
def query_filtered(sql_template: str, products: tuple, years: tuple) -> object:
    sql = sql_template.format(
        products=str_in_clause(list(products)),
        years=int_in_clause(list(years)),
    )
    return conn.query(sql, ttl=0)


@st.cache_data(ttl=600)
def query_company(sql_template: str, company: str) -> object:
    sql = sql_template.format(company=company.replace("'", "''"))
    return conn.query(sql, ttl=0)


@st.cache_data(ttl=3600)
def load_avg_dispute() -> float:
    row = conn.query(SQL_AVG_DISPUTE, ttl=0).iloc[0]
    return float(row["AVG_DISPUTE_RATE"] or 0)
```

- [ ] **Step 3: Add sidebar and tab scaffold below the loaders**

Append to `dashboard/app.py`:

```python
# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")

all_products = load_products()
sel_products = st.sidebar.multiselect("Product", all_products, default=all_products)
if not sel_products:
    sel_products = all_products

all_years = load_years()
sel_years = st.sidebar.multiselect("Year", all_years, default=all_years)
if not sel_years:
    sel_years = all_years

products_t = tuple(sel_products)
years_t    = tuple(sel_years)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Fintech Consumer Analytics")
st.caption("CFPB Consumer Complaint Database · Snowflake + dbt")

tab1, tab2 = st.tabs(["📊 Complaint Trends", "🔍 Resolution Quality"])
```

- [ ] **Step 4: Commit**

```bash
git add dashboard/app.py
git commit -m "feat(dashboard): scaffold app with connection, SQL constants, sidebar, and tabs"
```

---

## Task 4: Tab 1 — Complaint Trends (Descriptive)

**Files:**
- Modify: `dashboard/app.py` — append Tab 1 content after the `tab1, tab2 = st.tabs(...)` line

- [ ] **Step 1: Append Tab 1 content to `dashboard/app.py`**

```python
# ── Tab 1: Complaint Trends ───────────────────────────────────────────────────
with tab1:

    # Chart 1: Monthly volume
    df_monthly = query_filtered(SQL_MONTHLY_VOLUME, products_t, years_t)
    if not df_monthly.empty:
        peak = df_monthly.loc[df_monthly["COMPLAINT_COUNT"].idxmax()]
        st.subheader(
            f"Complaint volume peaked in {peak['YEAR_MONTH']} "
            f"with {int(peak['COMPLAINT_COUNT']):,} complaints"
        )
        fig1 = px.line(
            df_monthly, x="YEAR_MONTH", y="COMPLAINT_COUNT",
            labels={"YEAR_MONTH": "Month", "COMPLAINT_COUNT": "Complaints"},
        )
        fig1.update_traces(line_color="#2563eb")
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # Chart 2: By product
    df_product = query_filtered(SQL_BY_PRODUCT, products_t, years_t)
    if not df_product.empty:
        top = df_product.iloc[0]
        st.subheader(
            f"'{top['PRODUCT_NAME']}' generates the most complaints "
            f"({int(top['COMPLAINT_COUNT']):,})"
        )
        fig2 = px.bar(
            df_product, x="COMPLAINT_COUNT", y="PRODUCT_NAME", orientation="h",
            labels={"COMPLAINT_COUNT": "Complaints", "PRODUCT_NAME": "Product"},
        )
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Chart 3: Submission channels
    df_channels = query_filtered(SQL_CHANNELS, products_t, years_t)
    if not df_channels.empty:
        total = int(df_channels["COMPLAINT_COUNT"].sum())
        web_count = int(
            df_channels.loc[df_channels["CHANNEL"] == "web", "COMPLAINT_COUNT"].sum()
        )
        web_pct = round(100 * web_count / total) if total > 0 else 0
        st.subheader(f"Web submissions account for {web_pct}% of all complaints")
        fig3 = px.bar(
            df_channels, x="COMPLAINT_COUNT", y="CHANNEL", orientation="h",
            labels={"COMPLAINT_COUNT": "Complaints", "CHANNEL": "Channel"},
        )
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)
```

- [ ] **Step 2: Run the app locally and verify Tab 1 renders**

```bash
streamlit run dashboard/app.py
```

Open `http://localhost:8501`. Click "📊 Complaint Trends". All three charts should appear. Check that sidebar filters update the charts.

- [ ] **Step 3: Commit**

```bash
git add dashboard/app.py
git commit -m "feat(dashboard): add Tab 1 complaint trends with 3 charts"
```

---

## Task 5: Tab 2 — Resolution Quality (Diagnostic)

**Files:**
- Modify: `dashboard/app.py` — append Tab 2 content

- [ ] **Step 1: Append Tab 2 content to `dashboard/app.py`**

```python
# ── Tab 2: Resolution Quality ─────────────────────────────────────────────────
with tab2:

    # Chart 4: Dispute rate by product
    df_dispute = query_filtered(SQL_DISPUTE_RATE, products_t, years_t)
    if not df_dispute.empty:
        worst = df_dispute.iloc[0]
        st.subheader(
            f"'{worst['PRODUCT_NAME']}' has the highest dispute rate "
            f"at {worst['DISPUTE_RATE_PCT']}%"
        )
        fig4 = px.bar(
            df_dispute, x="DISPUTE_RATE_PCT", y="PRODUCT_NAME", orientation="h",
            labels={"DISPUTE_RATE_PCT": "Dispute Rate (%)", "PRODUCT_NAME": "Product"},
        )
        fig4.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # Chart 5: Timely response rate by product
    df_timely = query_filtered(SQL_TIMELY_RATE, products_t, years_t)
    if not df_timely.empty:
        worst_t = df_timely.iloc[0]
        st.subheader(
            f"'{worst_t['PRODUCT_NAME']}' has the lowest timely response rate "
            f"at {worst_t['TIMELY_RATE_PCT']}%"
        )
        fig5 = px.bar(
            df_timely, x="TIMELY_RATE_PCT", y="PRODUCT_NAME", orientation="h",
            labels={"TIMELY_RATE_PCT": "Timely Response Rate (%)", "PRODUCT_NAME": "Product"},
        )
        fig5.update_layout(yaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    # Company drill-down
    all_companies = load_companies()
    greenlight_matches = [c for c in all_companies if "greenlight" in c.lower()]
    default_idx = all_companies.index(greenlight_matches[0]) if greenlight_matches else 0
    selected_company = st.selectbox("Select a company", all_companies, index=default_idx)

    df_metrics = query_company(SQL_COMPANY_METRICS, selected_company)
    df_issues  = query_company(SQL_COMPANY_ISSUES, selected_company)
    avg_dispute = load_avg_dispute()

    if not df_metrics.empty:
        row = df_metrics.iloc[0]
        company_dispute = float(row["DISPUTE_RATE_PCT"] or 0)
        company_timely  = float(row["TIMELY_RATE_PCT"] or 0)
        delta = round(company_dispute - avg_dispute, 1)
        direction = "above" if delta > 0 else "below"

        st.subheader(
            f"{selected_company} dispute rate is {abs(delta)}% {direction} "
            f"the dataset average ({avg_dispute}%)"
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Complaints", f"{int(row['TOTAL_COMPLAINTS']):,}")
        col2.metric(
            "Dispute Rate",
            f"{company_dispute}%",
            delta=f"{delta:+.1f}% vs avg",
            delta_color="inverse",
        )
        col3.metric("Timely Response Rate", f"{company_timely}%")

    if not df_issues.empty:
        st.write("**Top 5 Complaint Issues**")
        st.dataframe(
            df_issues.rename(columns={"ISSUE": "Issue", "COMPLAINT_COUNT": "Count"}),
            use_container_width=True,
            hide_index=True,
        )
```

- [ ] **Step 2: Run the app locally and verify Tab 2 renders**

```bash
streamlit run dashboard/app.py
```

Open `http://localhost:8501`. Click "🔍 Resolution Quality". Verify:
- Dispute rate bar chart renders
- Timely response rate bar chart renders
- Company selectbox defaults to Greenlight (or similar)
- Three metric cards appear
- Top 5 issues table appears

- [ ] **Step 3: Run all tests to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: 5 passed.

- [ ] **Step 4: Commit**

```bash
git add dashboard/app.py
git commit -m "feat(dashboard): add Tab 2 resolution quality with drill-down"
```

---

## Task 6: Deploy to Streamlit Community Cloud

**No code changes — deployment only.**

- [ ] **Step 1: Push all commits to `main`**

```bash
git push origin main
```

- [ ] **Step 2: Create Streamlit Community Cloud app**

1. Go to `https://share.streamlit.io`
2. Sign in with GitHub
3. Click **"New app"**
4. Repository: `brandon-dong/fintech-consumer-analytics`
5. Branch: `main`
6. Main file path: `dashboard/app.py`
7. Click **"Advanced settings"**

- [ ] **Step 3: Add Snowflake secrets in the Streamlit UI**

In the Secrets panel, paste exactly:

```toml
[connections.snowflake]
account   = "<your-account-locator>"
user      = "<your-username>"
password  = "<your-password>"
database  = "FINTECH_ANALYTICS"
warehouse = "basket_craft_wh"
role      = ""
```

- [ ] **Step 4: Deploy and verify**

Click **"Deploy"**. Wait ~2 minutes for the build. The public URL will be in the format:
`https://<your-app-name>.streamlit.app`

Open the URL. Verify both tabs load data from Snowflake. Copy the URL — it goes in the README.

- [ ] **Step 5: Update README with the live URL and a dashboard screenshot**

In `README.md`, replace the placeholder lines:

```markdown
## Live Dashboard

**URL:** https://<your-app-name>.streamlit.app
```

And add a screenshot under `## Dashboard Preview`:

```markdown
## Dashboard Preview

![Dashboard screenshot](docs/dashboard-preview.png)
```

Take a screenshot of the live dashboard, save it as `docs/dashboard-preview.png`.

- [ ] **Step 6: Final commit**

```bash
git add README.md docs/dashboard-preview.png
git commit -m "feat(dashboard): add live URL and preview screenshot to README"
git push origin main
```

---

## Rubric Checklist

| Requirement | Task | Status |
|---|---|---|
| Connected to Snowflake mart | Task 3 | - [ ] |
| Descriptive analytics view | Task 4 | - [ ] |
| Diagnostic analytics view | Task 5 | - [ ] |
| Interactive element (filters + tabs + selectbox) | Tasks 3–5 | - [ ] |
| Deployed with public URL | Task 6 | - [ ] |
| README updated | Task 6 | - [ ] |
