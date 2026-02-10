# My Transactions Project

This is a Data Engineering project designed to automate the ingestion of transaction data into a SQLite database.

## Project Overview
This project demonstrates a basic ETL (Extract, Transform, Load) pipeline. It focuses on taking raw transaction data from a CSV file and efficiently loading it into a structured SQL environment for further analysis.

## Core Components
* **Data Ingestion:** The `ingest_data.py` script reads raw data from CSV files using Python.
* **Database Management:** Data is stored in a local SQLite database (`warehouse.db`), providing a lightweight and efficient storage solution.
* **Error Handling:** The pipeline includes basic error logging to ensure data integrity during the ingestion process.

## Tech Stack
* **Language:** Python
* **Library:** Pandas
* **Database:** SQLite
* **Version Control:** Git & GitHub

## How to Run
1. Clone the repository.
2. Ensure you have the `pandas` library installed.
3. Run the script located in the `scripts/` folder:
   ```bash
   python scripts/ingest_data.py
## Future Improvements
* **Visualization:** Connect the SQLite database to Power BI or Tableau for real-time dashboarding.
* **Cloud Integration:** Migrate the database to AWS S3 or Google BigQuery for cloud-scale processing.
* **Scheduling:** Use Airflow or Cron jobs to automate the script execution on a daily basis.
## 📊 Live Demo
You can access the interactive dashboard here: 
[👉 Live Retail Analytics Dashboard](https://mytransactionsproject-9p3n64vvp4rxs8jpqk3cw5.streamlit.app)

## 🛠 Lessons Learned
* **Big Data Handling**: Solved GitHub's 100MB limit using ZIP compression.
* **Mac/Linux Compatibility**: Fixed the `__MACOSX` zip issue by using terminal-based compression.
* **Performance**: Implemented SQL-in-memory to ensure the app loads in under 5 seconds despite the large dataset.

* # 📊 Retail Analytics Dashboard
An end-to-end data engineering project using Python and SQL.

## 🚀 Live Demo
[ΕΔΩ ΒΑΛΕ ΤΟ LINK ΤΟΥ STREAMLIT ΣΟΥ]

## 🛠 Features
- **Dynamic Filtering:** Filter by Country to see localized trends.
- **In-Memory Processing:** Uses SQLite for fast data aggregation.
- **Time-Series Analysis:** Monthly sales growth visualization.
