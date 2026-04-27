# Overview — Fintech Consumer Analytics Knowledge Base

## What This Project Analyzes

This project analyzes the **CFPB Consumer Complaint Database** to surface consumer trust signals across fintech products and companies. The central business question: *Which fintech products and companies are losing consumer trust, and why?*

The pipeline ingests raw CFPB complaint data via REST API into Snowflake, transforms it into a star schema via dbt, and surfaces trends via a Streamlit dashboard.

## The CFPB Complaint Database

The Consumer Financial Protection Bureau collects complaints from consumers about financial products and services. Key characteristics:

- **Scale**: 6.8 million+ complaints sent to companies for response (as of Dec 2024); 4.6M+ about credit reporting alone
- **Publication rule**: Only published after the company responds OR after 15 days — whichever comes first. The database updates daily.
- **Not a census**: The database is not a statistical sample. Low complaint volume doesn't mean low harm; high volume may reflect company size, not poor practices.
- **Data access**: Available via CSV/JSON download or the CFPB Open Data API at `cfpb.github.io/api/ccdb/api.html`
- **Annual reporting**: CFPB reports complaint trends to Congress each spring. The 2023 report is the most recent in the knowledge base.

CFPB uses complaint data for three purposes: regulation, enforcement, and consumer education. For our pipeline, the database is a **lagging indicator of consumer harm** — complaint volume rises after companies develop poor practices, and may continue rising even when CFPB enforcement de-prioritizes a category.

## Greenlight Financial Technology

Greenlight is the **primary company of interest** for this project, targeting the Associate Data Analyst role at Greenlight.

- **Scale**: 6.5 million parents and kids using Greenlight; $700M+ saved by families
- **Product**: Debit card for kids and teens + family safety app. Plans start at $5.99/month for the whole family (up to 5 kids)
- **Revenue model**: Subscription, not interchange-dominant — families pay monthly for the full suite
- **CFPB product categories**: Greenlight complaints appear under "Credit card or prepaid card" and/or "Checking or savings account" depending on product feature involved
- **Regulatory exposure**: As a money services business handling children's accounts, complaint patterns are politically sensitive — issues affect a vulnerable population (minors)

## Regulatory Environment (2025–2026)

The CFPB is undergoing significant leadership shifts under the Trump administration (2025):
- Reduced enforcement prioritization in several categories
- "Humility Pledge" (Nov 2025) signals less aggressive supervision
- Some prior enforcement cases being withdrawn
- Remaining focus: servicemembers, veterans, and "pressing threats"
- **Key precedent**: Wise penalized $2.5M (Jan 2025) for advertising inaccurate fees in money transfer products — signals continued scrutiny of fee transparency in fintech

**Implication for analysis**: Complaint filing by consumers continues independently of CFPB enforcement posture. Our pipeline captures consumer-initiated complaints regardless of regulatory activity — making the data a robust signal even in periods of regulatory pullback.

## Sources: cfpb_about_us.md, cfpb_complaint_database_overview.md, cfpb_bureau_by_the_numbers.md, cfpb_newsroom_recent_enforcement.md, greenlight_homepage.md, greenlight_how_it_works.md
