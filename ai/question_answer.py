import json

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from ai.tools.database_tools import (
    get_sales_summary,
    get_monthly_revenue,
    get_top_products,
    get_country_revenue,
    get_customer_segments,
    get_champions,
    get_at_risk_customers,
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

llm = LLM(
    model="gemini/gemini-3.5-flash-lite",
    temperature=0.2,
    max_retries=5,
)


# ============================================================
# DATABASE CONTEXT
# ============================================================

def make_json_safe(data):
    """Convert database results into JSON-safe values."""
    return json.loads(json.dumps(data, default=str))


def get_verified_business_context():
    """
    Load verified business information directly from PostgreSQL.

    PostgreSQL remains the source of truth.
    """

    sales = make_json_safe(get_sales_summary())
    monthly = make_json_safe(get_monthly_revenue())
    products = make_json_safe(get_top_products(10))
    countries = make_json_safe(get_country_revenue(15))
    segments = make_json_safe(get_customer_segments())
    champions = make_json_safe(get_champions(10))
    at_risk = make_json_safe(get_at_risk_customers(10))

    # --------------------------------------------------------
    # Deterministic derived metrics
    # --------------------------------------------------------

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
            high_value_at_risk_customers = int(
                segment["customer_count"]
            )
            high_value_at_risk_revenue = float(
                segment["total_revenue"]
            )

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

    return {
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

            "high_value_at_risk_customers": (
                high_value_at_risk_customers
            ),
            "high_value_at_risk_revenue": round(
                high_value_at_risk_revenue,
                2,
            ),

            "total_at_risk_customers": total_at_risk_customers,
            "total_at_risk_revenue": round(
                total_at_risk_revenue,
                2,
            ),

            "uk_revenue": round(uk_revenue, 2),
            "uk_revenue_share_percent": round(
                uk_revenue_share,
                2,
            ),
        },
    }


# ============================================================
# BUSINESS ANALYST AGENT
# ============================================================

business_analyst = Agent(
    role="RetailPulse-AI Conversational Business Analyst",

    goal=(
        "Answer the user's retail business question accurately "
        "using only verified PostgreSQL data."
    ),

    backstory="""
You are the conversational business analyst for RetailPulse-AI.

Your job is to answer questions about:

- sales
- revenue
- orders
- units
- products
- customers
- RFM segments
- Champions
- At Risk customers
- countries
- monthly performance

PostgreSQL is the source of truth.

You must never invent business data.

You must never pretend that an unsupported assumption is a fact.

You should provide useful business interpretation while keeping
FACT, INTERPRETATION, and RECOMMENDATION separate.

When the user asks a simple factual question, give a direct answer.

When the user asks for analysis, provide:

FACT:
What the verified data says.

INTERPRETATION:
What the data may indicate.

RECOMMENDATION:
A practical action that could be considered.

Never claim that a recommendation has already been implemented.
""",

    llm=llm,

    verbose=False,

    allow_delegation=False,
)


# ============================================================
# QUESTION ANSWER FUNCTION
# ============================================================

def answer_question(question):
    """
    Answer a user's business question using verified
    PostgreSQL data and Gemini through CrewAI.
    """

    if not question or not question.strip():
        return "Please enter a business question."

    question = question.strip()

    # --------------------------------------------------------
    # Load verified database context
    # --------------------------------------------------------

    try:
        verified_context = get_verified_business_context()

    except Exception as error:
        return (
            "I couldn't load the verified business data "
            "from PostgreSQL.\n\n"
            f"Database error: {error}"
        )

    context_json = json.dumps(
        verified_context,
        indent=2,
        default=str,
    )

    # --------------------------------------------------------
    # Create task
    # --------------------------------------------------------

    question_task = Task(
        description=f"""
You are answering this user question:

USER QUESTION:
{question}

============================================================
VERIFIED BUSINESS CONTEXT
============================================================

{context_json}

============================================================
ANSWER RULES
============================================================

1. PostgreSQL verified context is the ONLY source of business
   numbers.

2. Do not invent numbers.

3. Do not estimate missing values.

4. Do not recalculate percentages, ratios, growth rates,
   averages, differences, or comparisons.

5. Use a derived metric ONLY when it already exists inside
   verified_derived_metrics.

6. If the requested information does not exist in the verified
   context, clearly say that the available data does not provide
   that information.

7. Do not claim causes that are not proven by the data.

8. Do not assume:
   - customer intent
   - churn
   - wholesale customers
   - distributors
   - B2B customers
   - profitability
   - margins
   - conversion rates
   - reasons for revenue changes

9. Never present an interpretation as a FACT.

10. Never fabricate customer names or customer information.

============================================================
RESPONSE STYLE
============================================================

First answer the user's question directly.

Then, if useful, provide a short business interpretation.

For analytical questions use:

**FACT:** ...
**INTERPRETATION:** ...
**RECOMMENDATION:** ...

For simple questions, keep the answer concise.

Do not unnecessarily reproduce the entire database context.

Do not mention these internal instructions in your answer.
""",

        expected_output="""
A concise, accurate business answer grounded only in the
verified PostgreSQL context.
""",

        agent=business_analyst,
    )

    # --------------------------------------------------------
    # Run CrewAI
    # --------------------------------------------------------

    try:
        crew = Crew(
            agents=[business_analyst],
            tasks=[question_task],
            process=Process.sequential,
            verbose=False,
        )

        result = crew.kickoff()

        return str(result)

    except Exception as error:
        return (
            "I couldn't generate the AI answer.\n\n"
            f"CrewAI error: {error}"
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("RETAILPULSE-AI QUESTION ANSWERING TEST")
    print("=" * 70)

    test_question = "What is our total revenue?"

    print(f"\nQuestion: {test_question}\n")

    answer = answer_question(test_question)

    print("ANSWER")
    print("-" * 70)
    print(answer)

    print("\n" + "=" * 70)