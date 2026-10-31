import pandas as pd
import sqlite3
from pathlib import Path

from database import get_connection, initialize_database


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "sales.csv"


def load_sales_data():

    if not CSV_PATH.exists():
        raise FileNotFoundError("sales.csv file not found!")

    df = pd.read_csv(CSV_PATH)

    df.columns = df.columns.str.strip()

    required_columns = [
        "Transaction_Id",
        "Order_date",
        "Product",
        "Category",
        "Region",
        "Sales_channel",
        "Quantity",
        "Unit_price",
        "Discount_amount",
        "Status"
    ]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing CSV columns: {missing_columns}")

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM data_quality_issues")

    loaded_count = 0
    issue_count = 0

    for _, row in df.iterrows():

        issues = []

        transaction_id = (
            str(row["Transaction_Id"]).strip()
            if pd.notna(row["Transaction_Id"])
            else ""
        )

        if not transaction_id or transaction_id.lower() == "nan":
            continue

        # Validate date
        try:
            order_date = pd.to_datetime(
                row["Order_date"],
                format="%d-%m-%Y",
                errors="raise"
            ).strftime("%Y-%m-%d")

        except (ValueError, TypeError):
            order_date = None
            issues.append("Missing or invalid order date")

        # Validate quantity
        quantity = None

        try:
            if pd.notna(row["Quantity"]):
                quantity = int(row["Quantity"])

                if quantity < 0:
                    quantity = None
                    issues.append("Negative quantity")

                elif quantity == 0:
                    issues.append("Zero quantity")

            else:
                issues.append("Missing quantity")

        except (ValueError, TypeError, OverflowError):
            issues.append("Invalid quantity")

        # Validate unit price
        unit_price = None

        try:
            if pd.notna(row["Unit_price"]):
                unit_price = float(row["Unit_price"])

                if unit_price < 0:
                    unit_price = None
                    issues.append("Negative unit price")

            else:
                issues.append("Missing unit price")

        except (ValueError, TypeError, OverflowError):
            issues.append("Invalid unit price")

        # Validate discount
        discount_amount = None

        try:
            if pd.notna(row["Discount_amount"]):
                discount_amount = float(row["Discount_amount"])

                if discount_amount < 0:
                    discount_amount = None
                    issues.append("Negative discount")

            else:
                issues.append("Missing discount")

        except (ValueError, TypeError, OverflowError):
            issues.append("Invalid discount")

        # Validate text fields
        text_fields = [
            "Product",
            "Category",
            "Region",
            "Sales_channel",
            "Status"
        ]

        text_values = {}

        for field in text_fields:

            value = row[field]

            if pd.isna(value) or str(value).strip() == "":
                text_values[field] = None
                issues.append(f"Missing or empty {field}")

            else:
                text_values[field] = str(value).strip()

        # Store quality issues
        for issue in issues:

            cursor.execute(
                """
                INSERT INTO data_quality_issues
                (transaction_id, issue_description)
                VALUES (?, ?)
                """,
                (transaction_id, issue)
            )

            issue_count += 1

        # Insert transaction even if some fields are missing
        try:

            cursor.execute(
                """
                INSERT INTO sales (
                    transaction_id,
                    order_date,
                    product,
                    category,
                    region,
                    sales_channel,
                    quantity,
                    unit_price,
                    discount_amount,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction_id,
                    order_date,
                    text_values["Product"],
                    text_values["Category"],
                    text_values["Region"],
                    text_values["Sales_channel"],
                    quantity,
                    unit_price,
                    discount_amount,
                    text_values["Status"]
                )
            )

            loaded_count += 1

        except sqlite3.IntegrityError:

            cursor.execute(
                """
                INSERT INTO data_quality_issues
                (transaction_id, issue_description)
                VALUES (?, ?)
                """,
                (transaction_id, "Duplicate transaction ID")
            )

            issue_count += 1

    connection.commit()
    connection.close()

    print("CSV loading completed!")
    print("Total CSV records:", len(df))
    print("Successfully loaded:", loaded_count)
    print("Quality issues found:", issue_count)


if __name__ == "__main__":
    load_sales_data()