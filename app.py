import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Retail Data Dashboard", layout="wide")

st.title("📊 Retail Analytics Dashboard")
st.markdown("### Interactive Analysis of Kaggle Transactions")

# Διαδρομή για το ZIP αρχείο
zip_path = "data/transaction_data.csv.zip"


@st.cache_resource
def setup_database():
    """Διαβάζει το ZIP και δημιουργεί μια προσωρινή βάση SQL στη μνήμη"""
    # Το pandas μπορεί να διαβάσει το zip απευθείας!
    df = pd.read_csv(zip_path)

    # Δημιουργία σύνδεσης στη μνήμη (RAM) για ταχύτητα
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("data", conn, index=False, if_exists="replace")
    return conn


try:
    conn = setup_database()

    # SQL Query για τα Top Products
    query = """
    SELECT ItemDescription, 
           SUM(NumberOfItemsPurchased * CostPerItem) as total_sales
    FROM data
    GROUP BY ItemDescription
    ORDER BY total_sales DESC
    LIMIT 10;
    """
    df_top = pd.read_sql_query(query, conn)

    # Layout με Columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Top 10 Products by Revenue")
        st.table(df_top)

    with col2:
        st.subheader("Revenue Visualization")
        fig, ax = plt.subplots()
        ax.barh(df_top["ItemDescription"], df_top["total_sales"], color="#0077b6")
        ax.invert_yaxis()
        ax.set_xlabel("Total Sales ($)")
        st.pyplot(fig)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info(
        "Make sure 'data/transaction_data.csv.zip' exists in your GitHub repository."
    )
