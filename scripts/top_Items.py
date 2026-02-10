import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# We use the absolute path to ensure we are pointing to the correct database
db_path = "/Users/thomastotosis/Desktop/My_data_project/database/warehouse.db"


def analyze_and_plot():
    try:
        conn = sqlite3.connect(db_path)

        # We calculate the amount (quantity * unit price) if the column does not already exist
        # Here we use the columns you provided: NumberofItemsPurchased * CostPerItem
        query = """
        SELECT ItemDescription, 
               SUM(NumberOfItemsPurchased * CostPerItem) as total_sales
        FROM raw_transactions
        GROUP BY ItemDescription
        ORDER BY total_sales DESC
        LIMIT 5;
        """
        # NOTE: If your table is called 'transaction_data' change the 'FROM raw_transactions' to 'FROM transaction_data'

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print(
                "❌ The database appears to be empty. Please run ingest_data.py first!"
            )
            return

        print("--- Top 5 Products by Revenue ---")
        print(df)

        # Create Plot
        plt.figure(figsize=(12, 6))
        plt.barh(df["ItemDescription"], df["total_sales"], color="teal")
        plt.xlabel("Total Revenue ($)")
        plt.ylabel("Product Name")
        plt.title("Top 5 Best Selling Products")
        plt.gca().invert_yaxis()  # To have the first one on top
        plt.tight_layout()

        # Save
        plt.savefig(
            "/Users/thomastotosis/Desktop/My_data_project/top_products_chart.png"
        )
        plt.show()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    analyze_and_plot()
