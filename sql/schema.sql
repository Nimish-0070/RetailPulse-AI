CREATE TABLE IF NOT EXISTS dim_product (
    product_key SERIAL PRIMARY KEY,
    stock_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);



CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE,
    country VARCHAR(100)
);



CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    day INTEGER,
    day_of_week INTEGER
);



CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,

    invoice VARCHAR(50) NOT NULL,

    product_key INTEGER REFERENCES dim_product(product_key),

    customer_key INTEGER REFERENCES dim_customer(customer_key),

    date_key INTEGER REFERENCES dim_date(date_key),

    quantity INTEGER NOT NULL,

    unit_price NUMERIC(12, 4) NOT NULL,

    revenue NUMERIC(14, 4) NOT NULL,

    country VARCHAR(100)
);