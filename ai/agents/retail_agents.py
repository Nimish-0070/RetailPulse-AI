from crewai import Agent
from crewai.llm import LLM

from ai.tools.crew_tools import (
    sales_summary_tool,
    monthly_revenue_tool,
    top_products_tool,
    country_revenue_tool,
    customer_segments_tool,
    champions_tool,
    at_risk_customers_tool,
)


# ============================================================
# GEMINI
# ============================================================

llm = LLM(
    model="gemini/gemini-3.5-flash-lite",
    temperature=0.2,
    max_retries=5,
)


# ============================================================
# SALES AGENT
# ============================================================

sales_agent = Agent(
    role="Retail Sales Analyst",
    goal=(
        "Analyze RetailPulse sales performance using verified "
        "PostgreSQL data and identify important sales trends."
    ),
    backstory=(
        "You are an experienced retail sales analyst. "
        "You work only with verified database data and never "
        "invent business numbers."
    ),
    llm=llm,
    tools=[
        sales_summary_tool,
        monthly_revenue_tool,
    ],
    verbose=True,
)


# ============================================================
# PRODUCT AGENT
# ============================================================

product_agent = Agent(
    role="Product Performance Analyst",
    goal=(
        "Analyze product performance and identify products "
        "that contribute significantly to retail revenue."
    ),
    backstory=(
        "You specialize in retail product analytics. "
        "You analyze revenue, units sold, and orders using "
        "verified RetailPulse database information."
    ),
    llm=llm,
    tools=[
        top_products_tool,
    ],
    verbose=True,
)


# ============================================================
# CUSTOMER AGENT
# ============================================================

customer_agent = Agent(
    role="Customer Analytics Specialist",
    goal=(
        "Analyze customer behavior and RFM segments, including "
        "Champions and At-Risk customers."
    ),
    backstory=(
        "You are a customer analytics specialist who uses "
        "RFM segmentation to understand customer value and "
        "retention opportunities."
    ),
    llm=llm,
    tools=[
        customer_segments_tool,
        champions_tool,
        at_risk_customers_tool,
    ],
    verbose=True,
)


# ============================================================
# COUNTRY AGENT
# ============================================================

country_agent = Agent(
    role="Geographic Sales Analyst",
    goal=(
        "Analyze sales performance across countries and "
        "identify important geographic revenue patterns."
    ),
    backstory=(
        "You specialize in international retail analytics "
        "and analyze country-level revenue, orders, and units."
    ),
    llm=llm,
    tools=[
        country_revenue_tool,
    ],
    verbose=True,
)


# ============================================================
# BUSINESS ANALYST
# ============================================================

business_analyst_agent = Agent(
    role="Senior Retail Business Analyst",
    goal=(
        "Combine sales, product, customer, and country analysis "
        "into clear executive-level business insights."
    ),
    backstory=(
        "You are a senior retail business analyst. "
        "You turn verified analytics into useful business insights. "
        "You never fabricate numbers. Numerical claims must be "
        "supported by the supplied analysis."
    ),
    llm=llm,
    verbose=True,
)