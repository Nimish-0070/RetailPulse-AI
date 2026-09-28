from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

MERCHANDISE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "merchandise_data.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_rfm.csv"
)


def load_merchandise_data():
    """Load the cleaned merchandise dataset."""

    print(f"Loading: {MERCHANDISE_FILE}")

    df = pd.read_csv(
        MERCHANDISE_FILE,
        parse_dates=["InvoiceDate"]
    )

    return df


def calculate_rfm(df):
    """Calculate Recency, Frequency and Monetary metrics."""

    # Customer ID is required for customer-level RFM analysis
    customer_data = df.dropna(
        subset=["Customer_ID"]
    ).copy()

    # Use the latest transaction date as the analysis reference date
    reference_date = customer_data["InvoiceDate"].max()

    rfm = (
        customer_data
        .groupby("Customer_ID")
        .agg(
            Recency=(
                "InvoiceDate",
                lambda x: (
                    reference_date - x.max()
                ).days
            ),
            Frequency=(
                "Invoice",
                "nunique"
            ),
            Monetary=(
                "Revenue",
                "sum"
            )
        )
        .reset_index()
    )

    return rfm


def calculate_rfm_scores(rfm):
    """Calculate RFM quintile scores using PostgreSQL-style NTILE(5)."""

    def assign_ntile(df, column, ascending=True):
        """
        Reproduce PostgreSQL NTILE(5) behavior.

        Customers are ordered by the RFM metric and Customer_ID
        is used as a deterministic tie-breaker.
        """

        ordered = df.sort_values(
            by=[column, "Customer_ID"],
            ascending=[ascending, True]
        ).copy()

        n = len(ordered)

        # PostgreSQL NTILE(5)
        ordered["_position"] = range(1, n + 1)

        ordered["score"] = (
            ((ordered["_position"] - 1) * 5) // n
        ) + 1

        return ordered["score"].astype(int)

    # Recency:
    # PostgreSQL:
    # NTILE(5) OVER (ORDER BY recency DESC)
    #
    # Most recent customers should receive the highest R score.
    rfm["R_Score"] = assign_ntile(
        rfm,
        "Recency",
        ascending=False
    )

    # Frequency:
    # PostgreSQL:
    # NTILE(5) OVER (ORDER BY frequency)
    #
    # Higher frequency = higher score.
    rfm["F_Score"] = assign_ntile(
        rfm,
        "Frequency",
        ascending=True
    )

    # Monetary:
    # PostgreSQL:
    # NTILE(5) OVER (ORDER BY monetary)
    #
    # Higher monetary value = higher score.
    rfm["M_Score"] = assign_ntile(
        rfm,
        "Monetary",
        ascending=True
    )

    # Combined RFM score
    rfm["RFM_Score"] = (
        rfm["R_Score"].astype(int).astype(str)
        + rfm["F_Score"].astype(int).astype(str)
        + rfm["M_Score"].astype(int).astype(str)
    )

    return rfm


def assign_segments(rfm):
    """Assign customers to RFM segments."""

    def segment_customer(row):

        r = int(row["R_Score"])
        f = int(row["F_Score"])
        m = int(row["M_Score"])

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"

        elif r >= 4 and f >= 3:
            return "Loyal Customers"

        elif r >= 4 and m >= 4:
            return "High Value - Recent"

        elif r <= 2 and f >= 3:
            return "At Risk"

        elif r <= 2 and m >= 3:
            return "High Value - At Risk"

        elif r >= 3 and f <= 2:
            return "Potential Customers"

        else:
            return "Other"

    rfm["Customer_Segment"] = rfm.apply(
        segment_customer,
        axis=1
    )

    return rfm


def save_rfm(rfm):
    """Save customer RFM dataset."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    rfm.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Saved: {OUTPUT_FILE}")


def print_summary(rfm):
    """Print RFM summary statistics."""

    print("\n--- RFM Summary ---")

    print(f"Customers: {len(rfm):,}")

    print(
        f"Median Recency: "
        f"{rfm['Recency'].median():.0f} days"
    )

    print(
        f"Median Frequency: "
        f"{rfm['Frequency'].median():.0f} orders"
    )

    print(
        f"Median Monetary: "
        f"{rfm['Monetary'].median():,.2f}"
    )

    print("\n--- Customer Segments ---")

    segment_summary = (
        rfm
        .groupby("Customer_Segment")
        .agg(
            customers=("Customer_ID", "count"),
            revenue=("Monetary", "sum")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    print(segment_summary)


def main():

    df = load_merchandise_data()

    rfm = calculate_rfm(df)

    rfm = calculate_rfm_scores(rfm)

    rfm = assign_segments(rfm)

    save_rfm(rfm)

    print_summary(rfm)


if __name__ == "__main__":
    main()