-- =========================================================
-- RetailPulse-AI
-- SQL Analytics Layer
-- =========================================================

-- 1. Monthly Revenue Trend
-- Shows monthly revenue, orders, and units sold.

SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(f.revenue) AS total_revenue,
    COUNT(DISTINCT f.invoice) AS total_orders,
    SUM(f.quantity) AS total_units
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
-- 2. Top 10 Products by Revenue
-- =========================================================

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
    p.description
ORDER BY
    total_revenue DESC
LIMIT 10;


-- =========================================================
-- 3. Country Performance
-- =========================================================

SELECT
    f.country,
    SUM(f.revenue) AS total_revenue,
    SUM(f.quantity) AS total_units,
    COUNT(DISTINCT f.invoice) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_customers
FROM fact_sales f
GROUP BY
    f.country
ORDER BY
    total_revenue DESC;





-- =========================================================
-- 4. Customer Revenue & Order Analysis
-- Excludes transactions where Customer ID is unavailable
-- =========================================================

SELECT
    c.customer_id,
    c.country,
    COUNT(DISTINCT f.invoice) AS total_orders,
    SUM(f.quantity) AS total_units,
    SUM(f.revenue) AS total_revenue,
    ROUND(
        SUM(f.revenue) / COUNT(DISTINCT f.invoice),
        2
    ) AS average_order_value
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_id,
    c.country
ORDER BY
    total_revenue DESC
LIMIT 20;


-- =========================================================
-- 5. Monthly Average Order Value
-- =========================================================

SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(f.revenue) AS total_revenue,
    COUNT(DISTINCT f.invoice) AS total_orders,
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
-- 6. Top 10 Products by Units Sold
-- =========================================================

SELECT
    p.stock_code,
    p.description,
    SUM(f.quantity) AS total_units,
    SUM(f.revenue) AS total_revenue,
    COUNT(DISTINCT f.invoice) AS total_orders
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.stock_code,
    p.description
ORDER BY
    total_units DESC
LIMIT 10;


-- =========================================================
-- 7. Repeat vs One-Time Customers
-- =========================================================

WITH customer_orders AS (
    SELECT
        f.customer_key,
        COUNT(DISTINCT f.invoice) AS total_orders
    FROM fact_sales f
    WHERE f.customer_key IS NOT NULL
    GROUP BY f.customer_key
)

SELECT
    CASE
        WHEN total_orders = 1 THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END AS customer_type,
    COUNT(*) AS customer_count,
    SUM(total_orders) AS total_orders
FROM customer_orders
GROUP BY
    CASE
        WHEN total_orders = 1 THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END
ORDER BY
    customer_count DESC;



-- =========================================================
-- 8. Customer Value Segmentation
-- =========================================================

WITH customer_metrics AS (
    SELECT
        f.customer_key,
        c.customer_id,
        c.country,
        COUNT(DISTINCT f.invoice) AS total_orders,
        SUM(f.quantity) AS total_units,
        SUM(f.revenue) AS total_revenue,
        MAX(d.full_date) AS last_purchase_date,
        MIN(d.full_date) AS first_purchase_date
    FROM fact_sales f
    JOIN dim_customer c
        ON f.customer_key = c.customer_key
    JOIN dim_date d
        ON f.date_key = d.date_key
    WHERE f.customer_key IS NOT NULL
    GROUP BY
        f.customer_key,
        c.customer_id,
        c.country
)

SELECT
    customer_id,
    country,
    total_orders,
    total_units,
    total_revenue,
    last_purchase_date,
    first_purchase_date,
    (last_purchase_date - first_purchase_date) AS customer_lifetime_days
FROM customer_metrics
ORDER BY
    total_revenue DESC
LIMIT 20;




-- =========================================================
-- 9. RFM Customer Metrics
-- =========================================================

WITH customer_rfm AS (
    SELECT
        c.customer_id,
        c.country,

        -- Recency: days since last purchase
        (DATE '2010-12-09' - MAX(d.full_date)) AS recency,

        -- Frequency: number of unique orders
        COUNT(DISTINCT f.invoice) AS frequency,

        -- Monetary: total customer revenue
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
)

SELECT
    customer_id,
    country,
    recency,
    frequency,
    ROUND(monetary, 2) AS monetary
FROM customer_rfm
ORDER BY
    monetary DESC
LIMIT 20;



-- =========================================================
-- 10. RFM Scoring
-- =========================================================

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
        
        -- Recency: lower is better
        NTILE(5) OVER (
            ORDER BY recency DESC
        ) AS r_score,

        -- Frequency: higher is better
        NTILE(5) OVER (
            ORDER BY frequency
        ) AS f_score,

        -- Monetary: higher is better
        NTILE(5) OVER (
            ORDER BY monetary
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
    CONCAT(r_score, f_score, m_score) AS rfm_score
FROM rfm_scores
ORDER BY
    monetary DESC
LIMIT 20;



-- =========================================================
-- 11. RFM Customer Segmentation
-- =========================================================

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
            ORDER BY recency DESC
        ) AS r_score,

        NTILE(5) OVER (
            ORDER BY frequency
        ) AS f_score,

        NTILE(5) OVER (
            ORDER BY monetary
        ) AS m_score

    FROM customer_rfm
),

customer_segments AS (
    SELECT
        *,

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

    FROM rfm_scores
)

SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(AVG(monetary), 2) AS avg_customer_revenue,
    ROUND(AVG(frequency), 2) AS avg_orders,
    ROUND(AVG(recency), 2) AS avg_recency_days
FROM customer_segments
GROUP BY
    customer_segment
ORDER BY
    total_revenue DESC;