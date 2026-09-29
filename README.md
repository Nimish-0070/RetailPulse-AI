# RetailPulse-AI

### End-to-End Retail Analytics & Customer Segmentation

RetailPulse-AI is an end-to-end retail analytics project that transforms transactional sales data into structured business insights using **Python, PostgreSQL, SQL, and Power BI**.

The project covers the complete analytics workflow:

**Data Cleaning → Data Quality Validation → Data Modeling → SQL Analytics → RFM Customer Segmentation → Power BI Dashboard → Business Insights**

---

## Project Snapshot

| Area | Details |
|---|---|
| Domain | Retail Analytics |
| Dataset | Online Retail II |
| Analysis Period | Dec 2009 – Dec 9, 2010 |
| Raw Transactions | 525,461 |
| Exact Duplicates Removed | 6,865 |
| Final Merchandise Transactions | 502,691 |
| RFM Customers | 4,296 |
| Merchandise Revenue | 9.84M |
| Merchandise Units | 5,807,143 |
| Merchandise Products | 4,248 |
| PostgreSQL Fact Rows | 502,691 |
| Power BI Orders | 20,657 |
| Power BI AOV | 476.51 |
| Database | PostgreSQL |
| BI Tool | Power BI |
| Programming | Python |
| Analytics | SQL + RFM |

---

## Project Overview

Retail businesses generate large volumes of transaction data, but raw transaction records do not directly provide actionable business insights.

RetailPulse-AI transforms retail transaction data into a structured analytical system that helps answer questions such as:

- How does revenue change over time?
- Which products generate the most revenue?
- Which countries contribute the most revenue?
- How many customers are actively purchasing?
- Which customers have high monetary value?
- Which customers may be at risk?
- How are customers distributed across RFM segments?

The project was developed as an end-to-end **Data Analytics / Business Intelligence portfolio project**.

---

## Business Problem

A retail transaction dataset contains individual invoices, products, quantities, prices, customers, and countries.

However, raw transactional data alone makes it difficult to understand:

- Overall sales performance
- Product-level performance
- Geographic revenue contribution
- Customer purchasing behavior
- Customer value
- Customer engagement

The objective of RetailPulse-AI is to build a reproducible analytics workflow that converts raw transaction data into structured data models, analytical views, customer segments, and an interactive dashboard.

---

## Project Objectives

1. Clean and validate raw retail transaction data.
2. Identify and remove exact duplicate records.
3. Handle missing product descriptions.
4. Analyze missing customer information.
5. Separate valid sales transactions from operational/service records.
6. Create a structured PostgreSQL analytical database.
7. Build reusable SQL analytics views.
8. Perform customer RFM analysis.
9. Segment customers using Recency, Frequency, and Monetary value.
10. Build an interactive Power BI dashboard.
11. Validate analytical results between Python and PostgreSQL.
12. Extract business insights from the analyzed data.

---

## Dataset

### Dataset

**Online Retail II**

The dataset contains retail transaction records with fields including:

- Invoice
- StockCode
- Description
- Quantity
- InvoiceDate
- Price
- Customer ID
- Country

### Analysis Period

**December 2009 – December 9, 2010**

> December 2010 is a partial month because the dataset ends on December 9, 2010.

The project analysis uses the **Year 2009-2010** worksheet from the original workbook.

---

## Data Cleaning & Quality

The raw dataset contained:

- **525,461** rows
- **6,865** exact duplicate rows
- Missing product descriptions
- Missing customer IDs
- Negative quantities
- Zero-price transactions
- Operational/service-related stock codes

### Duplicate Handling

Exact duplicate records were identified and removed.

```text
Raw rows:                   525,461
Exact duplicates:             6,865
Rows after deduplication:   518,596