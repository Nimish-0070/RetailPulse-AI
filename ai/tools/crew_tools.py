from crewai.tools import tool

from ai.tools.database_tools import (
    get_sales_summary,
    get_monthly_revenue,
    get_top_products,
    get_country_revenue,
    get_customer_segments,
    get_champions,
    get_at_risk_customers,
)


@tool("Get Sales Summary")
def sales_summary_tool() -> str:
    """Get total revenue, orders, units, and average order value."""
    return str(get_sales_summary())


@tool("Get Monthly Revenue")
def monthly_revenue_tool() -> str:
    """Get monthly revenue, orders, and units."""
    return str(get_monthly_revenue())


@tool("Get Top Products")
def top_products_tool(limit: int = 10) -> str:
    """Get the highest-revenue retail products."""
    return str(get_top_products(limit))


@tool("Get Country Revenue")
def country_revenue_tool(limit: int = 10) -> str:
    """Get revenue performance by country."""
    return str(get_country_revenue(limit))


@tool("Get Customer Segments")
def customer_segments_tool() -> str:
    """Get RFM customer segments with counts and revenue."""
    return str(get_customer_segments())


@tool("Get Champions")
def champions_tool(limit: int = 10) -> str:
    """Get high-value Champion customers."""
    return str(get_champions(limit))


@tool("Get At Risk Customers")
def at_risk_customers_tool(limit: int = 10) -> str:
    """Get customers classified as At Risk or High Value - At Risk."""
    return str(get_at_risk_customers(limit))