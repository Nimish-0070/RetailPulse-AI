from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "online_retail_II.xlsx"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_data():
    """Load the raw Online Retail II dataset."""
    print(f"Loading dataset: {RAW_FILE}")

    df = pd.read_excel(
    RAW_FILE,
    sheet_name="Year 2009-2010"
)

    print(f"Raw rows: {len(df):,}")

    return df


def clean_data(df):
    """Clean and standardize the raw retail dataset."""

    df = df.copy()

    # Standardize column names
    df.columns = [
        column.strip().replace(" ", "_")
        for column in df.columns
    ]

    # Remove exact duplicate rows
    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows removed: {duplicate_count:,}")

    df = df.drop_duplicates().copy()

    # Convert data types
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce"
    )

    # Recover missing descriptions using StockCode
    description_map = (
        df.dropna(subset=["Description"])
        .drop_duplicates("StockCode")
        .set_index("StockCode")["Description"]
    )

    missing_before = df["Description"].isna().sum()

    df["Description"] = (
        df["Description"]
        .fillna(df["StockCode"].map(description_map))
    )

    missing_after = df["Description"].isna().sum()

    recovered = missing_before - missing_after

    print(f"Missing descriptions before recovery: {missing_before:,}")
    print(f"Descriptions recovered: {recovered:,}")
    print(f"Missing descriptions remaining: {missing_after:,}")

    return df


def create_sales_data(df):
    """Create valid sales transactions."""

    sales_data = df[
        (df["Quantity"] > 0) &
        (df["Price"] > 0)
    ].copy()

    sales_data["Revenue"] = (
        sales_data["Quantity"] *
        sales_data["Price"]
    )

    return sales_data


def create_merchandise_data(sales_data):
    """Remove operational/service codes from merchandise analysis."""

    non_product_codes = [
        "M",
        "DOT",
        "POST"
    ]

    merchandise_data = sales_data[
        ~sales_data["StockCode"].isin(non_product_codes)
    ].copy()

    return merchandise_data


def save_outputs(sales_data, merchandise_data):
    """Save processed datasets."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    sales_file = PROCESSED_DIR / "sales_data.csv"
    merchandise_file = PROCESSED_DIR / "merchandise_data.csv"

    sales_data.to_csv(
        sales_file,
        index=False
    )

    merchandise_data.to_csv(
        merchandise_file,
        index=False
    )

    print(f"Saved: {sales_file}")
    print(f"Saved: {merchandise_file}")


def print_summary(sales_data, merchandise_data):
    """Print final dataset statistics."""

    print("\n--- Sales Data ---")
    print(f"Rows: {len(sales_data):,}")
    print(f"Orders: {sales_data['Invoice'].nunique():,}")
    print(f"Units: {sales_data['Quantity'].sum():,.0f}")
    print(f"Revenue: {sales_data['Revenue'].sum():,.2f}")

    print("\n--- Merchandise Data ---")
    print(f"Rows: {len(merchandise_data):,}")
    print(f"Orders: {merchandise_data['Invoice'].nunique():,}")
    print(f"Units: {merchandise_data['Quantity'].sum():,.0f}")
    print(f"Revenue: {merchandise_data['Revenue'].sum():,.2f}")
    print(
        f"Products: "
        f"{merchandise_data['StockCode'].nunique():,}"
    )


def main():
    df = load_data()

    df_clean = clean_data(df)

    sales_data = create_sales_data(df_clean)

    merchandise_data = create_merchandise_data(
        sales_data
    )

    save_outputs(
        sales_data,
        merchandise_data
    )

    print_summary(
        sales_data,
        merchandise_data
    )


if __name__ == "__main__":
    main()