# from turtle import color
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(page_title="Retail Data Dashboard", layout="wide")

st.title("Retail Analytics Dashboard")
st.markdown("### Advanced Analysis of Kaggle Transactions")
with st.expander("About this Project"):
    st.write(
        """
        This dashboard analyzes public retail transaction data sourced from **Kaggle**.
        It uses an **In-memory SQLite database** for real-time processing and is 
        hosted on **Streamlit Cloud**. All data is anonymized and intended for 
        analytical purposes.
    """
    )

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
    st.subheader(" Monthly Sales Trend")
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

    # 6. Customer Segmentation Insights
    st.divider()
    st.header("👤 Customer Segmentation Insights")

    # Fetch Data for Customer Analytics
    query_spenders = f"""
    SELECT UserId, 
           COUNT(TransactionId) as total_orders, 
           CAST(SUM(NumberOfItemsPurchased * CostPerItem) AS INT) as total_spent
    FROM data
    {where_clause}
    GROUP BY UserId
    HAVING UserId IS NOT NULL
    ORDER BY total_spent DESC
    LIMIT 10;
    """
    df_spenders = pd.read_sql_query(query_spenders, conn)

    # Metrics Cards
    col_m1, col_m2, col_m3 = st.columns(3)
    total_customers = pd.read_sql_query(
        f"SELECT COUNT(DISTINCT UserId) FROM data {where_clause}", conn
    ).iloc[0, 0]
    avg_spend = df_spenders["total_spent"].mean()

    col_m1.metric("Unique Customers", f"{total_customers:,}")
    col_m2.metric("Avg Top-10 Spend", f"${avg_spend:,.0f}")
    col_m3.metric("Top Customer ID", f"{df_spenders.iloc[0]['UserId']}")

    # Visual Layout for Spenders
    col_s1, col_s2 = st.columns([1, 1.5])

    with col_s1:
        st.subheader("Top 10 High-Value Table")
        st.dataframe(
            df_spenders.style.format({"total_spent": "${:,}", "total_orders": "{:,}"})
        )

    with col_s2:
        st.subheader("Customer Value vs. Order Frequency")

        # Φιλτράρουμε τον "Πελάτη -1" μόνο για το γράφημα για να μην χαλάει την κλίμακα
        df_plot = df_spenders[df_spenders["UserId"] != -1]

        fig3, ax3 = plt.subplots(figsize=(10, 6))

        # Scatter plot με κανονική (linear) κλίμακα
        scatter = ax3.scatter(
            df_plot["total_orders"],
            df_plot["total_spent"],
            c=df_plot["total_spent"],
            cmap="coolwarm",
            s=250,
            alpha=0.8,
            edgecolors="white",
            linewidth=1.5,
        )

        # Προσθήκη ετικετών (ID) πάνω από κάθε τελεία
        for i, txt in enumerate(df_plot["UserId"]):
            ax3.annotate(
                f"ID: {txt}",
                (df_plot["total_orders"].iat[i], df_plot["total_spent"].iat[i]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=10,
                fontweight="bold",
            )

        # Κανονικοί τίτλοι χωρίς δυνάμεις
        ax3.set_xlabel("Number of Orders")
        ax3.set_ylabel("Total Spent ($)")

        # Μορφοποίηση των αξόνων για να φαίνονται εκατομμύρια (π.χ. 80M αντί για 80000000)
        from matplotlib.ticker import FuncFormatter

        def millions(x, pos):
            return f"${x*1e-6:,.0f}M" if x >= 1e6 else f"${x:,.0f}"

        ax3.yaxis.set_major_formatter(FuncFormatter(millions))
        ax3.grid(True, linestyle="--", alpha=0.6)

        st.pyplot(fig3)

    # --- OPTIMIZED MARKET BASKET ANALYSIS ---
    st.divider()
    st.header("🛒 Market Basket Analysis (Product Pairing)")
    st.markdown(
        "Discover which products are frequently purchased together. *(Optimized for performance)*"
    )

    # Optimization: We use a subquery to limit data to the top 10,000 rows
    # or the filtered country to prevent memory crashes.
    query_basket = f"""
        WITH subdata AS (
            SELECT TransactionId, ItemDescription 
            FROM data 
            {where_clause}
            LIMIT 50000 
        )
        SELECT a.ItemDescription AS Item_A, b.ItemDescription AS Item_B, COUNT(*) as frequency
        FROM subdata a
        JOIN subdata b ON a.TransactionId = b.TransactionId AND a.ItemDescription < b.ItemDescription
        GROUP BY Item_A, Item_B
        ORDER BY frequency DESC
        LIMIT 10
    """

    try:
        df_basket = pd.read_sql_query(query_basket, conn)

        if not df_basket.empty:
            col_b1, col_b2 = st.columns([1, 1.2])
            with col_b1:
                st.subheader("Top 10 Product Pairs")
                st.dataframe(df_basket, use_container_width=True)
            with col_b2:
                st.subheader("Pairing Strength Visualization")
                fig4, ax4 = plt.subplots(figsize=(10, 6))
                pairs_labels = df_basket["Item_A"] + " \n+ " + df_basket["Item_B"]
                ax4.barh(pairs_labels, df_basket["frequency"], color="#e76f51")
                ax4.invert_yaxis()
                ax4.set_xlabel("Frequency")
                st.pyplot(fig4)
        else:
            st.warning("Not enough data to find pairs for the selected filters.")
    except Exception as basket_error:
        st.error(f"Could not process Market Basket Analysis: {basket_error}")

    # --- RFM ANALYSIS SECTION ---
    st.divider()
    st.header("🎯 Customer Segmentation (RFM Analysis)")
    st.markdown("Categorizing customers based on their buying behavior.")

    # SQL query to calculate R, F, M per customer
    # Note: We use '2011-12-10' as the reference date for this specific dataset
    query_rfm = f"""
        SELECT 
            UserId,
            CAST(JULIANDAY('2011-12-10') - JULIANDAY(MAX(TransactionTime)) AS INT) as Recency,
            COUNT(DISTINCT TransactionId) as Frequency,
            SUM(NumberOfItemsPurchased * CostPerItem) as Monetary
        FROM data
        {where_clause}
        GROUP BY UserId
        HAVING UserId IS NOT NULL
    """

    df_rfm = pd.read_sql_query(query_rfm, conn)

    # Simple logic to label customers
    def segment_customer(df):
        if df["Monetary"] > df_rfm["Monetary"].quantile(0.8) and df[
            "Frequency"
        ] > df_rfm["Frequency"].quantile(0.8):
            return "Champion"
        elif df["Recency"] > df_rfm["Recency"].quantile(0.8):
            return "At Risk"
        else:
            return "Standard"

    df_rfm["Segment"] = df_rfm.apply(segment_customer, axis=1)

    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        st.subheader("Customer Segments Distribution")
        segment_counts = df_rfm["Segment"].value_counts()
        fig5, ax5 = plt.subplots()
        ax5.pie(
            segment_counts,
            labels=segment_counts.index,
            autopct="%1.1f%%",
            colors=["#2a9d8f", "#e76f51", "#e9c46a"],
        )
        st.pyplot(fig5)

    with col_r2:
        st.subheader("Segment Details (Preview)")
        st.dataframe(df_rfm.sort_values(by="Monetary", ascending=False).head(10))

except Exception as e:
    st.error(f"Error: {e}")
