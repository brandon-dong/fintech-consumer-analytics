# Source: CFPB Consumer Response Annual Report 2023
# URL: https://www.consumerfinance.gov/data-research/research-reports/consumer-response-annual-report-2023/
# Scraped: 2026-04-27
# Full PDF: https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2023-03.pdf

## Consumer Response Annual Report — 2023

Published: March 29, 2024

This Congressionally-mandated annual report analyzes complaints submitted by consumers to the CFPB between January and December 2023.

## Key Context

The annual report is the primary regulatory document summarizing:
- Total complaint volume by product category
- Company response rates and timeliness
- Consumer dispute rates (% who rejected company responses)
- Geographic distribution of complaints
- Trends in complaint narratives

## Relevance to Consumer Analytics

The 2023 annual report is the primary benchmark for interpreting patterns in our CFPB complaint database. Key metrics from the report contextualize our pipeline's data:

- **Checking or savings account**: Consistently highest complaint volume among bank products
- **Credit card or prepaid card**: Second-highest volume
- **Money transfer/virtual currency/money service**: Fastest-growing category, driven by fintech apps (Venmo, Zelle, Cash App, Greenlight)
- **Mortgage**: Complaint spikes tied to interest rate increases in 2022-2023

## Complaint Resolution Metrics

The CFPB tracks two key quality signals visible in our data:
1. **Timely response rate**: Companies must respond within 15 days
2. **Consumer dispute rate**: Percentage of consumers who rejected the company's response — a direct measure of complaint resolution quality

High dispute rates signal consumers who felt their issue was not adequately resolved, making `consumer_disputed_flag` the most analytically valuable field in our mart layer.
