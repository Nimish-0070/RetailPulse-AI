-- =========================================================
-- RetailPulse-AI
-- Dashboard Analytics Views
-- =========================================================

-- =========================================================
-- 1. Monthly Sales View
-- =========================================================

CREATE OR REPLACE VIEW monthly_sales_view AS

SELECT
    d.year,
    d.month,
    d.month_name,

    SUM(f.revenue) AS total_revenue,

    COUNT(DISTINCT f.invoice) AS total_orders,

    SUM(f.quantity) AS total_units,

    ROUND(
        SUM(f.revenue) / COUNT(DISTINCT f.invoice),
        2
    ) AS average_order_value

FROM fact_sales f

JOIN dim_date d
    ON f.date_key = d.date_key

GROUP BY
    d.year,
    d.month,
    d.month_name

ORDER BY
    d.year,
    d.month;



-- =========================================================
-- 2. Product Performance View
-- =========================================================

CREATE OR REPLACE VIEW product_performance_view AS

SELECT
    p.stock_code,
    p.description,

    SUM(f.revenue) AS total_revenue,

    SUM(f.quantity) AS total_units,

    COUNT(DISTINCT f.invoice) AS total_orders

FROM fact_sales f

JOIN dim_product p
    ON f.product_key = p.product_key

GROUP BY
    p.stock_code,
    p.description;


-- =========================================================
-- 3. Country Performance View
-- =========================================================

CREATE OR REPLACE VIEW country_performance_view AS

SELECT
    f.country,

    SUM(f.revenue) AS total_revenue,

    SUM(f.quantity) AS total_units,

    COUNT(DISTINCT f.invoice) AS total_orders,

    COUNT(DISTINCT f.customer_key) AS unique_customers

FROM fact_sales f

GROUP BY
    f.country;



-- =========================================================
-- 4. Customer Performance View
-- =========================================================

CREATE OR REPLACE VIEW customer_performance_view AS

SELECT
    c.customer_id,
    c.country,

    COUNT(DISTINCT f.invoice) AS total_orders,

    SUM(f.quantity) AS total_units,

    SUM(f.revenue) AS total_revenue,

    ROUND(
        SUM(f.revenue) / COUNT(DISTINCT f.invoice),
        2
    ) AS average_order_value,

    MIN(d.full_date) AS first_purchase_date,

    MAX(d.full_date) AS last_purchase_date,

    (MAX(d.full_date) - MIN(d.full_date)) AS customer_lifetime_days

FROM fact_sales f

JOIN dim_customer c
    ON f.customer_key = c.customer_key

JOIN dim_date d
    ON f.date_key = d.date_key

WHERE f.customer_key IS NOT NULL

GROUP BY
    c.customer_id,
    c.country;


-- =========================================================
-- 5. Customer RFM View
-- =========================================================

CREATE OR REPLACE VIEW customer_rfm_view AS

WITH customer_rfm AS (
    SELECT
        c.customer_id,
        c.country,

        (DATE '2010-12-09' - MAX(d.full_date)) AS recency,

        COUNT(DISTINCT f.invoice) AS frequency,

        SUM(f.revenue) AS monetary

    FROM fact_sales f

    JOIN dim_customer c
        ON f.customer_key = c.customer_key

    JOIN dim_date d
        ON f.date_key = d.date_key

    WHERE f.customer_key IS NOT NULL

    GROUP BY
        c.customer_id,
        c.country
),

rfm_scores AS (
    SELECT
        *,
        
        NTILE(5) OVER (
            ORDER BY recency DESC, customer_id ASC
        ) AS r_score,

        NTILE(5) OVER (
            ORDER BY frequency ASC, customer_id ASC
        ) AS f_score,

        NTILE(5) OVER (
            ORDER BY monetary ASC, customer_id ASC
        ) AS m_score

    FROM customer_rfm
)
SELECT
    customer_id,
    country,
    recency,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score,
    f_score,
    m_score,

    CONCAT(r_score, f_score, m_score) AS rfm_score,

    CASE
        WHEN r_score >= 4
             AND f_score >= 4
             AND m_score >= 4
            THEN 'Champions'

        WHEN r_score >= 4
             AND f_score >= 3
            THEN 'Loyal Customers'

        WHEN r_score >= 4
             AND m_score >= 4
            THEN 'High Value - Recent'

        WHEN r_score <= 2
             AND f_score >= 3
            THEN 'At Risk'

        WHEN r_score <= 2
             AND m_score >= 3
            THEN 'High Value - At Risk'

        WHEN r_score >= 3
             AND f_score <= 2
            THEN 'Potential Customers'

        ELSE 'Other'
    END AS customer_segment

FROM rfm_scores;


-- =========================================================
-- 6. RFM Segment Summary View
-- =========================================================

CREATE OR REPLACE VIEW rfm_segment_summary_view AS

SELECT
    customer_segment,

    COUNT(*) AS customer_count,

    ROUND(
        SUM(monetary),
        2
    ) AS total_revenue,

    ROUND(
        AVG(monetary),
        2
    ) AS avg_customer_revenue,

    ROUND(
        AVG(frequency),
        2
    ) AS avg_orders,

    ROUND(
        AVG(recency),
        2
    ) AS avg_recency_days

FROM customer_rfm_view

GROUP BY
    customer_segment;