import streamlit as st
import plotly.express as px
import pandas as pd

from helpers import str_in_clause, int_in_clause

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
    SELECT LOWER(COALESCE(f.submitted_via, 'unknown')) AS channel,
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
    ORDER BY 2 DESC NULLS LAST
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
def load_avg_dispute() -> float | None:
    row = conn.query(SQL_AVG_DISPUTE, ttl=0).iloc[0]
    val = row["AVG_DISPUTE_RATE"]
    return None if pd.isna(val) else float(val)


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
    else:
        st.warning("No data for the selected filters.")

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
    else:
        st.warning("No data for the selected filters.")

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
    else:
        st.warning("No data for the selected filters.")

with tab2:

    # Chart 4: Dispute rate by product
    df_dispute = query_filtered(SQL_DISPUTE_RATE, products_t, years_t)
    df_dispute_valid = df_dispute[df_dispute["DISPUTE_RATE_PCT"].notna()]
    if not df_dispute_valid.empty:
        worst = df_dispute_valid.iloc[0]
        st.subheader(
            f"'{worst['PRODUCT_NAME']}' has the highest dispute rate "
            f"at {worst['DISPUTE_RATE_PCT']}%"
        )
        fig4 = px.bar(
            df_dispute_valid, x="DISPUTE_RATE_PCT", y="PRODUCT_NAME", orientation="h",
            labels={"DISPUTE_RATE_PCT": "Dispute Rate (%)", "PRODUCT_NAME": "Product"},
        )
        fig4.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info(
            "Consumer dispute rate data is not available. "
            "The CFPB discontinued collecting the 'consumer disputed' field in 2017, "
            "so this metric is absent from post-2017 complaint records."
        )

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
    else:
        st.warning("No data for the selected filters.")

    st.divider()

    # Company drill-down
    all_companies = load_companies()
    if not all_companies:
        st.warning("No company data found. Check that dbt mart models have run.")
    else:
        greenlight_matches = [c for c in all_companies if "greenlight" in c.lower()]
        default_idx = all_companies.index(greenlight_matches[0]) if greenlight_matches else 0
        selected_company = st.selectbox("Select a company", all_companies, index=default_idx)

        df_metrics = query_company(SQL_COMPANY_METRICS, selected_company)
        df_issues  = query_company(SQL_COMPANY_ISSUES, selected_company)
        avg_dispute = load_avg_dispute()

        if not df_metrics.empty:
            row = df_metrics.iloc[0]
            company_dispute = None if pd.isna(row["DISPUTE_RATE_PCT"]) else float(row["DISPUTE_RATE_PCT"])
            company_timely  = None if pd.isna(row["TIMELY_RATE_PCT"]) else float(row["TIMELY_RATE_PCT"])

            if company_dispute is not None and avg_dispute is not None:
                delta = round(company_dispute - avg_dispute, 1)
                if delta > 0:
                    direction_phrase = f"{abs(delta)}% above"
                elif delta < 0:
                    direction_phrase = f"{abs(delta)}% below"
                else:
                    direction_phrase = "equal to"
                st.subheader(
                    f"{selected_company} dispute rate is {direction_phrase} "
                    f"the dataset average ({avg_dispute}%)"
                )
            else:
                delta = None
                st.subheader(
                    f"{selected_company}: {int(row['TOTAL_COMPLAINTS']):,} total complaints "
                    f"(dispute rate data not available)"
                )

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Complaints", f"{int(row['TOTAL_COMPLAINTS']):,}")
            col2.metric(
                "Dispute Rate",
                f"{company_dispute}%" if company_dispute is not None else "N/A",
                delta=f"{delta:+.1f}% vs avg" if delta is not None else None,
                delta_color="inverse",
            )
            col3.metric("Timely Response Rate", f"{company_timely}%" if company_timely is not None else "N/A")
        else:
            st.warning(f"No complaint data found for {selected_company}.")

        if not df_issues.empty:
            st.write("**Top 5 Complaint Issues**")
            st.dataframe(
                df_issues.rename(columns={"ISSUE": "Issue", "COMPLAINT_COUNT": "Count"}),
                use_container_width=True,
                hide_index=True,
            )
