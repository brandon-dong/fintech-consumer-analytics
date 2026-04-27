# Key Entities — Companies, Products, and Regulatory Bodies

## Regulatory Bodies

### Consumer Financial Protection Bureau (CFPB)
- **Role**: Federal agency implementing and enforcing consumer financial law; operates the complaint database this project analyzes
- **Jurisdiction**: Consumer financial products (banking, credit cards, prepaid cards, money transfers, mortgages, student loans, etc.)
- **Enforcement track record**: $21B+ in consumer relief, $5B+ in civil money penalties (as of Dec 2024)
- **Complaint pipeline**: 6.8M+ complaints sent to companies; CFPB forwards each to the company for response, typically within 15 days
- **Data API**: `https://cfpb.github.io/api/ccdb/api.html` — the source for this project's extraction script
- **Current posture (2025–2026)**: Reduced enforcement under Trump administration; "Humility Pledge" signals pullback, but complaint collection continues

## Companies

### Greenlight Financial Technology (Primary Subject)
- **Product type**: Prepaid debit card + family finance app for children and teens
- **User base**: 6.5 million parents and kids
- **Plan pricing**: Starts at $5.99/month (up to 5 kids)
- **CFPB product categories**: "Credit card or prepaid card" and "Checking or savings account"
- **Financial literacy angle**: Positions itself as an educational platform (500+ blog posts, CFPB-aligned financial literacy content)
- **Safety features**: Location sharing, SOS alerts, crash detection (Infinity plan); explicitly does not sell personal data
- **Allowance data**: Average Greenlight weekly allowance in 2024 was $12.98 for ages 5–19 (range: $6.05 at age 5 to $30.14 at age 19)
- **Complaint sensitivity**: Complaints involving minors' accounts carry heightened reputational and regulatory risk

### Wise (formerly TransferWise)
- **Product type**: International money transfer / remittance
- **CFPB product category**: "Money transfer, virtual currency, or money service"
- **Enforcement history**: $2.5M penalty (Jan 2025) for advertising inaccurate fees and failing to disclose exchange rates; order amended May 2025
- **Relevance**: Demonstrates active CFPB scrutiny of fee transparency in digital transfer products

### FirstCash
- **Product type**: Pawn lending / consumer lending
- **Enforcement history**: $363M+ in relief (Jul 2025) for Military Lending Act violations — targeting servicemembers
- **Relevance**: Illustrates CFPB's continued focus on servicemember protections even amid general enforcement pullback

## Product Categories (CFPB Taxonomy)

The CFPB classifies complaints by product and sub-product. Key categories for this project:

| Product | Sub-products | Relevant Companies |
|---|---|---|
| Credit card or prepaid card | General-purpose prepaid card, Gift card | Greenlight and similar |
| Checking or savings account | Checking account, Savings account | Banks, neobanks |
| Money transfer, virtual currency, or money service | Domestic wire transfer, International money transfer | Wise, Venmo, PayPal |
| Mortgage | Conventional home mortgage | Traditional banks |
| Student loan | Federal student loan | Servicers |

## Financial Literacy Programs

### CFPB "Money as You Grow"
- **Purpose**: Age-appropriate financial literacy activities for families; government-backed
- **Coverage**: Young children (saving basics), school-age (budgeting, earning), teens (credit, banking, investing)
- **Research basis**: 1+ year study drawing from dozens of curricula and academic research
- **Connection to Greenlight**: Both target the same population (families teaching children financial literacy). Greenlight is the commercial delivery mechanism for what CFPB provides as public education.

## Analytical Fields in fact_complaints

The three core analytic flags driving dashboard insights:
- `timely_response_flag` — did the company respond within CFPB's 15-day window? (Boolean)
- `consumer_disputed_flag` — did the consumer dispute the company's resolution? (Boolean)
- `submitted_via` — complaint channel: web, phone, referral, postal mail, web referral

High `consumer_disputed_flag` = poor resolution quality. Low `timely_response_flag` = operational slowness.

## Sources: greenlight_homepage.md, greenlight_how_it_works.md, greenlight_safety_infinity_features.md, greenlight_allowance_by_age.md, cfpb_money_as_you_grow.md, cfpb_newsroom_recent_enforcement.md, cfpb_about_us.md, cfpb_api_documentation.md
