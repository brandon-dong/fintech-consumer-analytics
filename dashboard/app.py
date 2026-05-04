import streamlit as st
import plotly.express as px
import pandas as pd

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

# Company drill-down queries are intentionally year-agnostic — they show
# the company's full complaint history as a consistent benchmark.
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
def query_filtered(sql_template: str, products: tuple, years: tuple):
    sql = sql_template.format(
        products=str_in_clause(list(products)),
        years=int_in_clause(list(years)),
    )
    return conn.query(sql, ttl=0)


@st.cache_data(ttl=600)
def query_company(sql_template: str, company: str):
    sql = sql_template.format(company=company.replace("'", "''"))
    return conn.query(sql, ttl=0)


@st.cache_data(ttl=3600)
def load_avg_dispute() -> float:
    row = conn.query(SQL_AVG_DISPUTE, ttl=0).iloc[0]
    val = row["AVG_DISPUTE_RATE"]
    return 0.0 if pd.isna(val) else float(val)


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")

all_products = load_products()
if not all_products:
    st.error("No products found in Snowflake MART. Check your Snowflake connection and dbt models.")
    st.stop()

sel_products = st.sidebar.multiselect("Product", all_products, default=all_products)
if not sel_products:
    sel_products = all_products

all_years = load_years()
if not all_years:
    st.error("No years found in Snowflake MART. Check your Snowflake connection and dbt models.")
    st.stop()

sel_years = st.sidebar.multiselect("Year", all_years, default=all_years)
if not sel_years:
    sel_years = all_years

products_t = tuple(sel_products)
years_t    = tuple(sel_years)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Fintech Consumer Analytics")
st.caption("CFPB Consumer Complaint Database · Snowflake + dbt")

tab1, tab2 = st.tabs(["📊 Complaint Trends", "🔍 Resolution Quality"])

with tab1:
    st.info("Complaint Trends charts coming soon.")

with tab2:
    st.info("Resolution Quality charts coming soon.")
