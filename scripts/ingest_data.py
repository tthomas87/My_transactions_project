import pandas as pd
import sqlite3
import os

# Αυτό βρίσκει αυτόματα τη διαδρομή του script σου
current_script_path = os.path.abspath(__file__)
# Αυτό βρίσκει τον φάκελο 'scripts'
scripts_folder = os.path.dirname(current_script_path)
# Αυτό πηγαίνει ένα επίπεδο πάνω, στον κεντρικό φάκελο 'My_data_project'
base_project_path = os.path.dirname(scripts_folder)

# Τώρα ορίζουμε τις διαδρομές σωστά
csv_file = os.path.join(base_project_path, "data", "transaction_data.csv")
db_file = os.path.join(base_project_path, "database", "warehouse.db")


def run_ingestion():
    print(f"Checking for file at: {csv_file}")

    # Έλεγχος αν το αρχείο υπάρχει όντως εκεί
    if not os.path.exists(csv_file):
        print(f"❌ ERROR: Το αρχείο δεν βρέθηκε στο: {csv_file}")
        print(
            "Σιγουρέψου ότι το αρχείο μέσα στο φάκελο 'data' λέγεται ακριβώς 'transaction_data.csv'"
        )
        return

    try:
        print("Reading CSV...")
        df = pd.read_csv(csv_file)

        print("Connecting to SQLite...")
        conn = sqlite3.connect(db_file)

        # Φόρτωση στη βάση
        df.to_sql("raw_transactions", conn, if_exists="replace", index=False)
        conn.close()

        print(f"✅ Success! Data loaded into: {db_file}")
    except Exception as e:
        print(f"❌ Κάτι πήγε στραβά: {e}")


if __name__ == "__main__":
    run_ingestion()
