import os

from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError, DatabaseError


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "RetailPulse_DB")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a connection to the RetailPulse PostgreSQL database.

    Raises:
        ValueError: If DB_PASSWORD is missing.
        ConnectionError: If PostgreSQL cannot be reached.
    """

    if not DB_PASSWORD:
        raise ValueError(
            "DB_PASSWORD not found in .env. "
            "Please configure the PostgreSQL password."
        )

    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )

    except OperationalError as error:
        raise ConnectionError(
            "Unable to connect to PostgreSQL. "
            f"Check that PostgreSQL is running and the database "
            f"'{DB_NAME}' is available."
        ) from error


# ============================================================
# QUERY EXECUTION
# ============================================================

def run_query(query, params=None):
    """
    Execute a SQL query and return results as dictionaries.

    Args:
        query: SQL query string.
        params: Optional query parameters.

    Returns:
        List of dictionaries containing query results.

    Raises:
        ConnectionError: If the database connection fails.
        RuntimeError: If the SQL query fails.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)

            # Queries such as INSERT/UPDATE/DELETE may not
            # return a result set.
            if cursor.description is None:
                connection.commit()
                return []

            columns = [
                description[0]
                for description in cursor.description
            ]

            rows = cursor.fetchall()

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    except DatabaseError as error:
        connection.rollback()

        raise RuntimeError(
            "Database query failed. "
            "Please verify the database schema and SQL query."
        ) from error

    finally:
        connection.close()


# ============================================================
# VALIDATION
# ============================================================

def validate_limit(limit, default=10, maximum=100):
    """
    Validate a LIMIT value before passing it to PostgreSQL.

    This prevents invalid values from reaching the database.
    """

    if limit is None:
        return default

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return default

    if limit < 1:
        return default

    return min(limit, maximum)


# ============================================================
# SALES
# ============================================================

def get_total_revenue():
    """Get total merchandise revenue."""

    query = """
        SELECT
            ROUND(SUM(total_revenue)::numeric, 2) AS total_revenue
        FROM public.monthly_sales_view;
    """

    return run_query(query)


def get_sales_summary():
    """Get overall RetailPulse sales KPIs."""

    query = """
        SELECT
            ROUND(SUM(total_revenue)::numeric, 2) AS total_revenue,
            SUM(total_orders) AS total_orders,
            SUM(total_units) AS total_units,
            ROUND(
                (
                    SUM(total_revenue) /
                    NULLIF(SUM(total_orders), 0)
                )::numeric,
                2
            ) AS average_order_value
        FROM public.monthly_sales_view;
    """

    return run_query(query)


def get_monthly_revenue():
    """Get monthly revenue performance."""

    query = """
        SELECT
            year,
            month,
            month_name,
            ROUND(total_revenue::numeric, 2) AS revenue,
            total_orders,
            total_units
        FROM public.monthly_sales_view
        ORDER BY year, month;
    """

    return run_query(query)


# ============================================================
# PRODUCTS
# ============================================================

def get_top_products(limit=10):
    """Get top products ranked by revenue."""

    limit = validate_limit(limit, default=10)

    query = """
        SELECT
            stock_code,
            description,
            ROUND(total_revenue::numeric, 2) AS revenue,
            total_units,
            total_orders
        FROM public.product_performance_view
        ORDER BY total_revenue DESC
        LIMIT %s;
    """

    return run_query(query, (limit,))


def get_product_performance(limit=20):
    """Get product performance by revenue."""

    limit = validate_limit(limit, default=20)

    query = """
        SELECT
            stock_code,
            description,
            ROUND(total_revenue::numeric, 2) AS revenue,
            total_units,
            total_orders
        FROM public.product_performance_view
        ORDER BY total_revenue DESC
        LIMIT %s;
    """

    return run_query(query, (limit,))


# ============================================================
# COUNTRIES
# ============================================================

def get_country_revenue(limit=20):
    """Get revenue performance by country."""

    limit = validate_limit(limit, default=20)

    query = """
        SELECT
            country,
            ROUND(total_revenue::numeric, 2) AS revenue,
            total_units,
            total_orders
        FROM public.country_performance_view
        ORDER BY total_revenue DESC
        LIMIT %s;
    """

    return run_query(query, (limit,))


# ============================================================
# CUSTOMERS
# ============================================================

def get_customer_summary():
    """Get overall customer performance."""

    query = """
        SELECT
            COUNT(*) AS customers,
            ROUND(SUM(total_revenue)::numeric, 2) AS revenue,
            ROUND(
                AVG(total_revenue)::numeric,
                2
            ) AS average_customer_revenue
        FROM public.customer_performance_view;
    """

    return run_query(query)


def get_customer_segments():
    """Get customer segment counts, revenue, and RFM metrics."""

    query = """
        SELECT
            customer_segment,
            customer_count,
            ROUND(total_revenue::numeric, 2) AS total_revenue,
            ROUND(
                avg_customer_revenue::numeric,
                2
            ) AS avg_customer_revenue,
            ROUND(
                avg_orders::numeric,
                2
            ) AS avg_orders,
            ROUND(
                avg_recency_days::numeric,
                2
            ) AS avg_recency_days
        FROM public.rfm_segment_summary_view
        ORDER BY total_revenue DESC;
    """

    return run_query(query)


def get_rfm_summary():
    """Get complete RFM segment summary."""

    query = """
        SELECT
            customer_segment,
            customer_count,
            ROUND(total_revenue::numeric, 2) AS total_revenue,
            ROUND(
                avg_customer_revenue::numeric,
                2
            ) AS avg_customer_revenue,
            ROUND(
                avg_orders::numeric,
                2
            ) AS avg_orders,
            ROUND(
                avg_recency_days::numeric,
                2
            ) AS avg_recency_days
        FROM public.rfm_segment_summary_view
        ORDER BY customer_count DESC;
    """

    return run_query(query)


# ============================================================
# CUSTOMER SEGMENTS
# ============================================================

def get_at_risk_customers(limit=20):
    """Get customers classified as At Risk."""

    limit = validate_limit(limit, default=20)

    query = """
        SELECT
            customer_id,
            recency,
            frequency,
            monetary,
            customer_segment
        FROM public.customer_rfm_view
        WHERE customer_segment IN (
            'At Risk',
            'High Value - At Risk'
        )
        ORDER BY monetary DESC
        LIMIT %s;
    """

    return run_query(query, (limit,))


def get_champions(limit=20):
    """Get Champion customers."""

    limit = validate_limit(limit, default=20)

    query = """
        SELECT
            customer_id,
            recency,
            frequency,
            monetary,
            customer_segment
        FROM public.customer_rfm_view
        WHERE customer_segment = 'Champions'
        ORDER BY monetary DESC
        LIMIT %s;
    """

    return run_query(query, (limit,))


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("RetailPulse-AI Database Tools Test")
    print("=" * 60)

    try:

        print("\n1. Sales Summary")
        print(get_sales_summary())

        print("\n2. Top 5 Products")
        print(get_top_products(5))

        print("\n3. Top 5 Countries")
        print(get_country_revenue(5))

        print("\n4. Customer Segments")
        print(get_customer_segments())

        print("\n5. Champions")
        print(get_champions(5))

        print("\n6. At-Risk Customers")
        print(get_at_risk_customers(5))

        print("\n" + "=" * 60)
        print("Database tools test completed successfully.")
        print("=" * 60)

    except Exception as error:

        print("\n" + "=" * 60)
        print("DATABASE TEST FAILED")
        print("=" * 60)
        print(f"Error: {error}")
        print("=" * 60)