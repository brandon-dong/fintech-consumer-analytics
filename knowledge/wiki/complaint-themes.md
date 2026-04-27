# Complaint Themes — Cross-Source Synthesis

## How to Use This Page

This page synthesizes complaint patterns across CFPB regulatory context, Greenlight product knowledge, and prepaid card consumer rights. Use it to interpret why complaint spikes occur and which `dim_issue` values map to which business failures.

---

## Theme 1: Children Making Unauthorized Purchases (In-App / In-Game Spending)

**What it is**: Children or teens making purchases in games or apps without parental authorization. Often framed as the child bypassing parental controls, or the app bypassing CFPB fee disclosure requirements.

**Why it matters**: Greenlight's internet safety guide explicitly lists "pressure to spend money in games or apps" as a documented danger for children. This generates complaints under "Checking or savings account" and "Credit card or prepaid card" categories.

**Analytical signal**: High `consumer_disputed_flag` rate in prepaid card transactions involving minors. The CFPB considers unauthorized charges on prepaid cards a consumer rights violation — prepaid card regulations require card issuers to respond to unauthorized transaction disputes.

**Data fields**: `dim_product.product_name = 'Credit card or prepaid card'`, `dim_issue.issue` values around "Problem with a purchase shown on your statement" or "Unauthorized transactions."

---

## Theme 2: Account Access Failures

**What it is**: Consumers locked out of accounts — due to lost/stolen cards, family member departures from a plan, or account closure issues.

**Why it matters**: Greenlight's safety features (location sharing, SOS) are tied to account access. If a family member leaves the Infinity plan, data access and location history questions arise. Card loss or theft is a primary prepaid card complaint category per the CFPB consumer guide.

**Analytical signal**: `timely_response_flag = FALSE` is often correlated with account access issues, as these require manual resolution (not automated).

**Data fields**: `dim_issue.issue` values around "Managing an account" or "Problem getting a card or closing an account."

---

## Theme 3: Fee Transparency Failures

**What it is**: Companies advertising lower fees than they charge, or failing to disclose fees in required formats. The CFPB prepaid rule mandates fee disclosures.

**Why it matters**: The Wise enforcement action ($2.5M, Jan 2025) was specifically about advertising inaccurate fees and failing to disclose exchange rates. The same CFPB fee disclosure rules that apply to Wise's transfers apply to Greenlight's prepaid card maintenance, ATM, and card replacement fees.

**Common complaint fees**: Monthly maintenance, card replacement, ATM balance inquiry, foreign transaction, card-to-card transfer.

**Analytical signal**: Complaints about fees appear in the "Checking or savings account" or "Credit card or prepaid card" categories. Fee complaints correlate with high `consumer_disputed_flag` because consumers rarely accept "the fee was disclosed" as a resolution.

**Data fields**: `dim_issue.issue` values around "Unexpected or other fees" or "Fees or interest."

---

## Theme 4: Dispute Resolution Quality

**What it is**: Companies providing inadequate or dismissive responses to consumer disputes, prompting consumers to escalate to the CFPB via the `consumer_disputed_flag`.

**Why it matters**: This is the single most important metric in our schema. A company that closes disputes with "closed with explanation" but generates high `consumer_disputed_flag` rates is telling consumers "we explained it away" — not "we fixed it." High dispute rates signal systemic response quality failures, not just one-off errors.

**Greenlight context**: A $50 disputed transaction represents ~6 weeks of allowance for a 10-year-old (who gets $8.44/week on Greenlight). The financial impact is material to the family even if small in absolute terms — explaining elevated dispute rates for children's products.

**Analytical signal**: Compare `consumer_disputed_flag` rate by `company_response_to_consumer` value in `dim_company`. Companies with high dispute rates on "closed with explanation" responses are the most analytically interesting.

---

## Theme 5: Privacy and Safety Data Concerns

**What it is**: Concerns about location data, driving data, and crash detection information collected by family fintech safety features.

**Why it matters**: Greenlight's Infinity plan collects significant personal data (real-time location, driving behavior, crash events). Their privacy policy explicitly prohibits selling this data or sharing with auto insurers — but consumer complaints about data retention after account closure or unexpected data uses still occur.

**Analytical signal**: These complaints appear under "Checking or savings account" or may be filed as "Money transfer" complaints if tied to the payment product. Privacy complaints often have long lag time — consumers may not realize their data is at risk until after account closure.

---

## Theme 6: Regulatory Environment as Complaint Volume Modifier

**What it is**: CFPB enforcement posture affects complaint *resolution* rates, not complaint *filing* rates.

**Why it matters**: In the current DOGE-era regulatory environment (2025–2026), CFPB is deprioritizing enforcement in some categories. But consumers still file complaints independently. Our pipeline captures complaints as filed — making it a leading indicator of consumer harm even when enforcement is lagging.

**Analytical signal**: The ratio of complaints to regulatory actions may widen during enforcement pullback periods (2025+). Monitor complaint volume trends alongside CFPB newsroom releases to identify when the regulatory backstop has weakened.

---

## Complaint Volume Calibration

When interpreting complaint counts:
- Normalize by company size — Greenlight's 6.5M users will generate more raw complaints than a smaller competitor
- CFPB explicitly cautions: low volume ≠ low harm; consumers may not know to complain or may not blame the right company
- Use `consumer_disputed_flag` rate (not raw count) as the primary quality signal — it's normalized by the number of complaints that got a company response

## Sources: cfpb_prepaid_cards_consumer_guide.md, greenlight_internet_safety_guide.md, greenlight_allowance_by_age.md, cfpb_newsroom_recent_enforcement.md, greenlight_safety_infinity_features.md, cfpb_complaint_database_overview.md, cfpb_bureau_by_the_numbers.md
