# Data Quality Report

## Raw Dataset

Total raw records: 525,461

## 1. Duplicate Records

6,865 exact duplicate records were identified,
representing 1.31% of the raw dataset.

The duplicate records were identical across all
available fields.

One copy of each duplicate record was retained.

---

## 2. Missing Product Descriptions

Initially, 2,928 records had missing product descriptions.

Using StockCode, 2,563 descriptions were recovered
from other records containing the same StockCode.

365 records remained without a recoverable description.

These records were retained because StockCode still
provides product identification.

---

## 3. Missing Customer IDs

107,833 records had missing Customer IDs.

These records were not automatically removed because
Customer ID is not required for revenue or product-level
analysis.

Transactions without Customer IDs can still contribute
to valid sales analysis.

They will be excluded only from analyses that require
customer-level identification.

---

## 4. Non-Sales Transactions

Transactions with:

- Quantity <= 0
- Price <= 0

were excluded from the sales analysis dataset.

The original cleaned transaction dataset remains
available for audit and further investigation.

---

## 5. Final Sales Dataset

The sales dataset contains only records satisfying:

Quantity > 0
AND
Price > 0

Final sales records: 504,731

Total revenue: 10,272,136.23

Total orders: 20,952

Total products: 4,251