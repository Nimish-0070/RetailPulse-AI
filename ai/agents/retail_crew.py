import json
from crewai import Crew, Process, Task

from ai.agents.retail_agents import (
    sales_agent,
    product_agent,
    customer_agent,
    country_agent,
    business_analyst_agent,
)

from ai.tools.database_tools import (
    get_sales_summary,
    get_monthly_revenue,
    get_top_products,
    get_country_revenue,
    get_customer_segments,
    get_champions,
    get_at_risk_customers,
)


def make_json_safe(data):
    """
    Convert database results into JSON-safe values.
    Handles Decimal and other database-specific types.
    """
    return json.loads(json.dumps(data, default=str))


def get_verified_business_context():
    """
    Pull all important business metrics directly from PostgreSQL.

    These values are treated as the source of truth.
    """

    sales = make_json_safe(get_sales_summary())
    monthly = make_json_safe(get_monthly_revenue())
    products = make_json_safe(get_top_products(10))
    countries = make_json_safe(get_country_revenue(15))
    segments = make_json_safe(get_customer_segments())
    champions = make_json_safe(get_champions(5))
    at_risk = make_json_safe(get_at_risk_customers(5))

    # Deterministic calculations.
    # Gemini should NOT calculate these itself.

    champion_customers = 0
    champion_revenue = 0.0

    at_risk_customers = 0
    at_risk_revenue = 0.0

    high_value_at_risk_customers = 0
    high_value_at_risk_revenue = 0.0

    for segment in segments:
        name = segment["customer_segment"]

        if name == "Champions":
            champion_customers = int(segment["customer_count"])
            champion_revenue = float(segment["total_revenue"])

        elif name == "At Risk":
            at_risk_customers = int(segment["customer_count"])
            at_risk_revenue = float(segment["total_revenue"])

        elif name == "High Value - At Risk":
            high_value_at_risk_customers = int(segment["customer_count"])
            high_value_at_risk_revenue = float(segment["total_revenue"])

    total_at_risk_customers = (
        at_risk_customers + high_value_at_risk_customers
    )

    total_at_risk_revenue = (
        at_risk_revenue + high_value_at_risk_revenue
    )

    total_revenue = float(sales[0]["total_revenue"])

    uk_revenue = 0.0

    for country in countries:
        if country["country"] == "United Kingdom":
            uk_revenue = float(country["revenue"])
            break

    uk_revenue_share = (
        (uk_revenue / total_revenue) * 100
        if total_revenue
        else 0
    )

    verified = {
        "sales_summary": sales,
        "monthly_revenue": monthly,
        "top_products": products,
        "country_revenue": countries,
        "customer_segments": segments,
        "top_champions": champions,
        "top_at_risk_customers": at_risk,

        "verified_derived_metrics": {
            "champion_customers": champion_customers,
            "champion_revenue": round(champion_revenue, 2),

            "at_risk_customers": at_risk_customers,
            "at_risk_revenue": round(at_risk_revenue, 2),

            "high_value_at_risk_customers": high_value_at_risk_customers,
            "high_value_at_risk_revenue": round(
                high_value_at_risk_revenue, 2
            ),

            "total_at_risk_customers": total_at_risk_customers,
            "total_at_risk_revenue": round(
                total_at_risk_revenue, 2
            ),

            "uk_revenue": round(uk_revenue, 2),
            "uk_revenue_share_percent": round(
                uk_revenue_share, 2
            ),
        },
    }

    return verified


def main():

    print("\n" + "=" * 70)
    print("RETAILPULSE-AI — VERIFIED BUSINESS CONTEXT")
    print("=" * 70)

    verified_context = get_verified_business_context()

    # Convert verified database context into text for the final analyst.
    verified_context_json = json.dumps(
        verified_context,
        indent=2,
        default=str
    )

    print("\nVerified business context loaded from PostgreSQL.")

    # ---------------------------------------------------------
    # SPECIALIZED AGENT TASKS
    # ---------------------------------------------------------

    sales_task = Task(
        description="""
Analyze the sales performance of RetailPulse-AI.

Use the database tools to retrieve:
- total revenue
- total orders
- total units
- average order value
- monthly revenue

Focus on factual observations and business-relevant trends.

Do not invent numbers.
""",
        expected_output="""
A concise sales performance analysis containing verified
metrics and important monthly trends.
""",
        agent=sales_agent,
    )

    product_task = Task(
        description="""
Analyze product performance.

Use the database tools to identify the top revenue-generating
products.

Report the product names, revenue, units and orders where
available.

Do not invent or estimate numbers.
""",
        expected_output="""
A concise product performance analysis based on database results.
""",
        agent=product_agent,
    )

    customer_task = Task(
        description="""
Analyze customer behavior using RFM segmentation.

Use the database tools to analyze:
- customer segments
- Champions
- At Risk customers
- High Value - At Risk customers

Do not invent customer counts or revenue values.
""",
        expected_output="""
A concise customer/RFM analysis based on PostgreSQL data.
""",
        agent=customer_agent,
    )

    country_task = Task(
        description="""
Analyze geographic revenue performance.

Use the database tools to identify the countries generating
the highest revenue.

Do not invent or estimate numbers.
""",
        expected_output="""
A concise geographic revenue analysis based on database results.
""",
        agent=country_agent,
    )

    # ---------------------------------------------------------
    # FINAL BUSINESS ANALYST
    # ---------------------------------------------------------

    business_task = Task(
    description=f"""
You are the Senior Business Analyst for RetailPulse-AI.

Create the final executive business analysis using ONLY the
VERIFIED BUSINESS CONTEXT provided below.

The database is the source of truth.

============================================================
STRICT NUMERICAL RULES
============================================================

1. Use ONLY numbers explicitly present in VERIFIED BUSINESS CONTEXT.

2. Copy numerical values exactly.

3. DO NOT recalculate numbers yourself.

4. DO NOT calculate:
   - percentages
   - ratios
   - growth rates
   - differences
   - averages
   - shares
   - "over half"
   - "majority"
   - "more than"
   - any other derived numerical relationship

5. If a derived metric is needed, use it ONLY if it already
   exists inside "verified_derived_metrics".

6. Never invent, estimate, round differently, or modify a number.

7. If another agent gives a conflicting number, ignore it and
   use the VERIFIED BUSINESS CONTEXT.

============================================================
FACT / INTERPRETATION / RECOMMENDATION
============================================================

Every important business insight must clearly separate:

FACT
-----
A FACT must come directly from the verified database context.

Example:

**FACT:** Champions contain 908 customers and generated
$5,567,539.20 in revenue.

Do not add assumptions to a FACT.

------------------------------------------------------------

INTERPRETATION
--------------

An INTERPRETATION explains what the facts may indicate.

Use cautious language such as:

- "This suggests..."
- "This may indicate..."
- "This pattern is consistent with..."
- "This could warrant further investigation..."

Never present an interpretation as a proven fact.

------------------------------------------------------------

RECOMMENDATION
--------------

A RECOMMENDATION is a proposed business action.

Clearly label it as a recommendation.

Examples:

- "Consider a win-back campaign..."
- "Review inventory planning..."
- "Investigate regional order patterns..."

Do not claim that a recommendation has already been implemented.

============================================================
STRICT INTERPRETATION RULES
============================================================

Do NOT present any of the following as established facts unless
the VERIFIED BUSINESS CONTEXT explicitly proves them:

- customer churn
- customer intent
- reasons for churn
- reasons for revenue changes
- causes of seasonal patterns
- wholesale customers
- distributors
- B2B customers
- pallet shipments
- profitability
- margins
- conversion rates
- market growth
- future revenue
- financial stability
- demand causes
- revenue leakage
- dormancy as a confirmed customer state
- causal relationships

For example:

BAD:
"Denmark consists of wholesale distributor shipments."

GOOD:
"Denmark generated $50,348.85 from 25 orders and
229,659 units. This suggests unusually high units per order
and may warrant investigation into the characteristics of
those orders."

============================================================
NO UNSUPPORTED NUMERICAL COMPARISONS
============================================================

Do NOT write statements such as:

- "Champions generate over half of revenue."
- "The UK generates the majority of revenue."
- "Revenue increased by X%."
- "Orders grew by X%."
- "This segment is X times larger."
- "This represents X% of customers."

UNLESS that exact derived metric already exists in the
VERIFIED BUSINESS CONTEXT.

Instead, state the underlying verified facts separately.

============================================================
VERIFIED BUSINESS CONTEXT
============================================================

{json.dumps(verified_context, indent=2)}

============================================================
REQUIRED OUTPUT FORMAT
============================================================

# RetailPulse-AI Executive Business Analysis

## 1. Executive Summary

Provide 3–5 concise observations.

For each observation:

**FACT:** ...

**INTERPRETATION:** ...

**RECOMMENDATION:** ...

---

## 2. Sales Performance

### Facts
Report verified sales metrics and observed monthly patterns.

### Interpretations
Explain what the patterns may indicate without claiming
unverified causes.

### Recommendations
Suggest practical evidence-based actions.

---

## 3. Product Performance

### Facts
Report verified product metrics.

### Interpretations
Explain observable product patterns without inventing
customer motivations.

### Recommendations
Suggest inventory, promotion, cross-selling, or investigation
actions where appropriate.

---

## 4. Customer & RFM Insights

### Facts
Report verified customer segment counts, revenue, recency,
and frequency.

### Interpretations
Explain what the RFM patterns may indicate.

### Recommendations
Suggest retention, win-back, loyalty, or customer-development
actions.

---

## 5. Geographic Performance

### Facts
Report verified country-level revenue, orders, and units.

### Interpretations
Explain observable geographic patterns.

### Recommendations
Suggest areas for investigation or commercial action.

Do NOT label countries as wholesale, B2B, distributor-driven,
or similar unless explicitly proven by the data.

---

## 6. Business Opportunities

For every opportunity:

**FACT:** ...

**INTERPRETATION:** ...

**RECOMMENDATION:** ...

Keep recommendations practical and evidence-based.

---

## 7. Key Takeaways

Provide 4–6 concise bullets.

Each bullet must clearly be labeled:

- FACT
- INTERPRETATION
- RECOMMENDATION

============================================================
FINAL QUALITY CHECK
============================================================

Before producing the answer verify:

1. Every number exists in VERIFIED BUSINESS CONTEXT.
2. No numbers were recalculated.
3. No unsupported percentages or ratios were created.
4. No "over half", "majority", growth rate, or similar
   derived comparison was invented.
5. FACT, INTERPRETATION, and RECOMMENDATION are clearly separated.
6. No causal claim is presented as a fact.
7. No unsupported claims about wholesale, B2B, distributors,
   churn, profitability, margins, or customer intent.
8. Recommendations are clearly presented as suggestions.
9. The report is concise and professional enough for a
   portfolio project and interview demonstration.
""",
    expected_output="""
A professional executive business analysis with strict
separation between FACT, INTERPRETATION, and RECOMMENDATION,
using only verified database information.
""",
        agent=business_analyst_agent,
    )

    # ---------------------------------------------------------
    # CREW
    # ---------------------------------------------------------

    retail_crew = Crew(
        agents=[
            sales_agent,
            product_agent,
            customer_agent,
            country_agent,
            business_analyst_agent,
        ],
        tasks=[
            sales_task,
            product_task,
            customer_task,
            country_task,
            business_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    print("\n" + "=" * 70)
    print("STARTING RETAILPULSE-AI CREW")
    print("=" * 70)

    result = retail_crew.kickoff()

    print("\n" + "=" * 70)
    print("FINAL BUSINESS ANALYSIS")
    print("=" * 70)

    print(result)


if __name__ == "__main__":
    main()
