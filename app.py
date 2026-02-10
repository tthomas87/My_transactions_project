import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(page_title="Retail Data Dashboard", layout="wide")

st.title("📊 Retail Analytics Dashboard")
st.markdown("### Advanced Analysis of Kaggle Transactions")

zip_path = "data/transaction_data.csv.zip"


@st.cache_resource
def setup_database():
    df = pd.read_csv(zip_path)
    # Μετατροπή της ημερομηνίας σε σωστό format για την SQL
    df["TransactionTime"] = pd.to_datetime(df["TransactionTime"]).dt.strftime(
        "%Y-%m-%d"
    )
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("data", conn, index=False, if_exists="replace")
    return conn


try:
    conn = setup_database()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
    # Παίρνουμε τη λίστα με τις χώρες για το φίλτρο
    countries = pd.read_sql_query(
        "SELECT DISTINCT Country FROM data ORDER BY Country", conn
    )["Country"].tolist()
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries)

    # Κατασκευή του WHERE clause βάσει του φίλτρου
    where_clause = (
        "" if selected_country == "All" else f"WHERE Country = '{selected_country}'"
    )

    # --- QUERY 1: TOP PRODUCTS ---
    query_top = f"""
    SELECT ItemDescription, 
           CAST(SUM(NumberOfItemsPurchased * CostPerItem) AS INT) as total_sales
    FROM data
    {where_clause}
    GROUP BY ItemDescription
    ORDER BY total_sales DESC
    LIMIT 10;
    """
    df_top = pd.read_sql_query(query_top, conn)

    # --- QUERY 2: SALES OVER TIME (BY MONTH) ---
    query_time = f"""
    SELECT strftime('%Y-%m', TransactionTime) as Month,
           CAST(SUM(NumberOfItemsPurchased * CostPerItem) AS INT) as Monthly_Sales
    FROM data
    {where_clause}
    GROUP BY Month
    ORDER BY Month;
    """
    df_time = pd.read_sql_query(query_time, conn)

    # --- DISPLAY LAYOUT ---

    # Πρώτη σειρά: Top Products Table & Bar Chart
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(f"Top 10 Products ({selected_country})")
        st.table(df_top)

    with col2:
        st.subheader("Revenue Visualization")
        fig1, ax1 = plt.subplots()
        ax1.barh(df_top["ItemDescription"], df_top["total_sales"], color="#0077b6")
        ax1.invert_yaxis()
        ax1.set_xlabel("Total Sales ($)")
        st.pyplot(fig1)

    # Δεύτερη σειρά: Time Series Chart
    st.divider()
    st.subheader("📅 Monthly Sales Trend")
    if not df_time.empty:
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        ax2.plot(
            df_time["Month"],
            df_time["Monthly_Sales"],
            marker="o",
            linestyle="-",
            color="#e63946",
        )
        ax2.set_ylabel("Sales ($)")
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    else:
        st.write("No time data available for this selection.")

except Exception as e:
    st.error(f"Error: {e}")
