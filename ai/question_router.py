from ai.tools.database_tools import (
    get_sales_summary,
    get_monthly_revenue,
    get_top_products,
    get_country_revenue,
    get_customer_segments,
    get_champions,
    get_at_risk_customers,
)

from ai.question_answer import answer_question


# ============================================================
# SIMPLE QUESTION KEYWORDS
# ============================================================

SIMPLE_PATTERNS = [
    "total revenue",
    "revenue",
    "total sales",
    "sales",

    "total orders",
    "orders",
    "how many orders",
    "number of orders",
    "order count",

    "total units",
    "units sold",
    "units",
    "how many units",
    "number of units",

    "average order value",
    "aov",

    "top products",
    "best products",
    "highest revenue products",
    "which products generate the most revenue",
    "which products generate most revenue",
    "products generate the most revenue",

    "top countries",
    "countries",
    "highest revenue countries",
    "which country generates the most revenue",
    "which country generates most revenue",
    "country generates the most revenue",
    "country generates most revenue",

    "customer segments",
    "segments",
    "champions",
    "at risk customers",
    "customers at risk",
]


# ============================================================
# DETERMINE QUESTION TYPE
# ============================================================

def is_simple_question(question):
    """
    Determine whether the question can be answered directly
    from PostgreSQL.
    """

    question_lower = question.lower().strip()

    analytical_words = [
        "why",
        "how did",
        "how has",
        "recommend",
        "recommendation",
        "suggest",
        "explain",
        "reason",
        "insight",
        "strategy",
        "opportunity",
        "trend",
        "analyze",
        "analysis",
    ]

    # Analytical questions always go to CrewAI + Gemini.
    for word in analytical_words:
        if word in question_lower:
            return False

    # Simple factual questions.
    simple_patterns = [
        "total revenue",
        "revenue",
        "total sales",
        "sales",

        "total orders",
        "how many orders",
        "number of orders",
        "order count",

        "total units",
        "units sold",
        "how many units",
        "number of units",

        "average order value",
        "aov",

        "top products",
        "best products",
        "highest revenue products",
        "which products generate the most revenue",
        "which products generate most revenue",
        "products generate the most revenue",

        "top countries",
        "highest revenue countries",
        "which country generates the most revenue",
        "which country generates most revenue",
        "country generates the most revenue",
        "country generates most revenue",

        "customer segments",
        "segments",

        "champions",

        "at risk customers",
        "customers at risk",
    ]

    return any(
        pattern in question_lower
        for pattern in simple_patterns
    )


# ============================================================
# FORMAT CURRENCY
# ============================================================

def format_currency(value):
    """Format a number as currency."""

    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


# ============================================================
# DIRECT SQL ANSWERS
# ============================================================

def direct_sql_answer(question):
    """
    Answer simple factual questions directly from PostgreSQL.
    """

    question_lower = question.lower().strip()

    # --------------------------------------------------------
    # TOTAL REVENUE / SALES SUMMARY
    # --------------------------------------------------------

    if (
        "total revenue" in question_lower
        or question_lower == "revenue"
    ):

        data = get_sales_summary()[0]

        return (
            "**FACT:** Total revenue is "
            f"**{format_currency(data['total_revenue'])}**."
        )

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    if (
        "total orders" in question_lower
        or question_lower == "orders"
    ):

        data = get_sales_summary()[0]

        return (
            "**FACT:** Total orders are "
            f"**{int(data['total_orders']):,}**."
        )

    # --------------------------------------------------------
    # UNITS
    # --------------------------------------------------------

    if (
        "total units" in question_lower
        or "units sold" in question_lower
        or question_lower == "units"
    ):

        data = get_sales_summary()[0]

        return (
            "**FACT:** Total units sold are "
            f"**{int(data['total_units']):,}**."
        )

    # --------------------------------------------------------
    # AOV
    # --------------------------------------------------------

    if (
        "average order value" in question_lower
        or "aov" in question_lower
    ):

        data = get_sales_summary()[0]

        return (
            "**FACT:** Average Order Value (AOV) is "
            f"**{format_currency(data['average_order_value'])}**."
        )

    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    if (
        "top products" in question_lower
        or "best products" in question_lower
        or "highest revenue products" in question_lower
        or "which products generate the most revenue" in question_lower
        or "which products generate most revenue" in question_lower
        or "products generate the most revenue" in question_lower
    ):

        products = get_top_products(5)

        if not products:
            return (
                "**FACT:** No product performance data "
                "is currently available."
            )

        lines = [
            "**FACT:** Top products by revenue:\n"
        ]

        for index, product in enumerate(products, start=1):

            # Clean trailing/leading whitespace from
            # database product descriptions before
            # inserting them into Markdown.
            description = str(
                product.get("description", "")
            ).strip()

            if not description:
                description = "Unnamed Product"

            lines.append(
                f"{index}. **{description}** — "
                f"{format_currency(product['revenue'])}"
            )

        return "\n".join(lines)

    # --------------------------------------------------------
    # COUNTRIES
    # --------------------------------------------------------

    if (
        "top countries" in question_lower
        or question_lower == "countries"
        or "highest revenue countries" in question_lower
        or "which country generates the most revenue" in question_lower
        or "which country generates most revenue" in question_lower
        or "country generates the most revenue" in question_lower
        or "country generates most revenue" in question_lower
    ):

        countries = get_country_revenue(5)

        if not countries:
            return (
                "**FACT:** No country performance data "
                "is currently available."
            )

        lines = [
            "**FACT:** Top countries by revenue:\n"
        ]

        for index, country in enumerate(
            countries,
            start=1,
        ):

            country_name = str(
                country.get("country", "")
            ).strip()

            if not country_name:
                country_name = "Unknown Country"

            lines.append(
                f"{index}. **{country_name}** — "
                f"{format_currency(country['revenue'])}"
            )

        return "\n".join(lines)

    # --------------------------------------------------------
    # CUSTOMER SEGMENTS
    # --------------------------------------------------------

    if (
        "customer segments" in question_lower
        or question_lower == "segments"
    ):

        segments = get_customer_segments()

        if not segments:
            return (
                "**FACT:** No customer segment data "
                "is currently available."
            )

        lines = [
            "**FACT:** Customer segment summary:\n"
        ]

        for segment in segments:

            segment_name = str(
                segment.get("customer_segment", "")
            ).strip()

            if not segment_name:
                segment_name = "Unknown Segment"

            lines.append(
                f"- **{segment_name}**: "
                f"{int(segment['customer_count']):,} customers"
            )

        return "\n".join(lines)

    # --------------------------------------------------------
    # CHAMPIONS
    # --------------------------------------------------------

    if "champions" in question_lower:

        champions = get_champions(5)

        if not champions:
            return (
                "**FACT:** No Champion customer data "
                "is currently available."
            )

        lines = [
            "**FACT:** Top Champion customers:\n"
        ]

        for customer in champions:

            lines.append(
                f"- Customer **{customer['customer_id']}** — "
                f"Revenue: "
                f"{format_currency(customer['monetary'])}"
            )

        return "\n".join(lines)

    # --------------------------------------------------------
    # AT-RISK CUSTOMERS
    # --------------------------------------------------------

    if (
        "at risk customers" in question_lower
        or "customers at risk" in question_lower
    ):

        customers = get_at_risk_customers(5)

        if not customers:
            return (
                "**FACT:** No at-risk customer data "
                "is currently available."
            )

        lines = [
            "**FACT:** Top at-risk customers:\n"
        ]

        for customer in customers:

            lines.append(
                f"- Customer **{customer['customer_id']}** — "
                f"Revenue: "
                f"{format_currency(customer['monetary'])}"
            )

        return "\n".join(lines)

    return None


# ============================================================
# VISUALIZATION DETECTION
# ============================================================

def get_visualization_type(question):
    """
    Detect whether the user is asking for a visual representation.

    Returns:
        'monthly_revenue'
        'top_products'
        'country_revenue'
        'customer_segments'
        None
    """

    question_lower = question.lower().strip()

    chart_words = [
        "show me",
        "show",
        "chart",
        "graph",
        "visual",
        "visualize",
        "plot",
        "trend",
    ]

    wants_visual = any(
        word in question_lower
        for word in chart_words
    )

    if not wants_visual:
        return None

    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "monthly revenue",
            "revenue by month",
            "revenue trend",
            "monthly sales",
        ]
    ):
        return "monthly_revenue"

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "top products",
            "best products",
            "product revenue",
            "products by revenue",
            "highest revenue products",
            "which products generate the most revenue",
        ]
    ):
        return "top_products"

    # --------------------------------------------------------
    # COUNTRIES
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "country revenue",
            "revenue by country",
            "sales by country",
            "country performance",
            "highest revenue countries",
            "which country generates the most revenue",
            "which country generates most revenue",
            "country generates the most revenue",
            "country generates most revenue",
        ]
    ):
        return "country_revenue"

    # --------------------------------------------------------
    # CUSTOMER SEGMENTS
    # --------------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "customer segments",
            "customer segment",
            "segments",
            "rfm segments",
        ]
    ):
        return "customer_segments"

    return None


# ============================================================
# MAIN ROUTER
# ============================================================

def route_question(question):
    """
    Route the question to either:

    1. Direct PostgreSQL
    2. CrewAI + Gemini

    The router also provides a controlled fallback message
    when either data or AI services fail.
    """

    if not question or not question.strip():
        return "Please enter a business question."

    question = question.strip()

    # --------------------------------------------------------
    # SIMPLE QUESTION → DIRECT SQL
    # --------------------------------------------------------

    if is_simple_question(question):

        try:

            result = direct_sql_answer(question)

            if result is not None:
                return result

            return (
                "I couldn't find a direct database answer "
                "for that question."
            )

        except Exception:

            return (
                "I couldn't retrieve the requested data "
                "from PostgreSQL.\n\n"
                "Please check that the database is running "
                "and try again."
            )

    # --------------------------------------------------------
    # ANALYTICAL QUESTION → CREWAI + GEMINI
    # --------------------------------------------------------

    try:

        result = answer_question(question)

        # Protect the application from empty AI responses.
        if result is None:
            return (
                "I couldn't generate an AI analysis for "
                "that question."
            )

        if not isinstance(result, str):
            result = str(result)

        if not result.strip():
            return (
                "I couldn't generate an AI analysis for "
                "that question."
            )

        return result

    except Exception:

        return (
            "The AI analysis service is temporarily unavailable.\n\n"
            "Please try again in a moment. "
            "Your database and project data are not affected."
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_questions = [
        "What is our total revenue?",
        "How many orders do we have?",
        "Which products generate the most revenue?",
        "Which country generates the most revenue?",
        "Why did revenue change during the year?",
    ]

    print("=" * 70)
    print("RETAILPULSE-AI QUESTION ROUTER TEST")
    print("=" * 70)

    for question in test_questions:

        print("\nQUESTION:")
        print(question)

        if is_simple_question(question):
            print("ROUTE: DIRECT POSTGRESQL")
        else:
            print("ROUTE: CREWAI + GEMINI")

        print("-" * 70)