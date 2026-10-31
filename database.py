import sqlite3
from pathlib import Path

# Get the project folder location
BASE_DIR = Path(__file__).resolve().parent

# Database file location
DB_PATH = BASE_DIR / "sales.db"


# Connect to the database
def get_connection(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)

    # Allows us to access columns using their names
    connection.row_factory = sqlite3.Row

    return connection


# Create the required database tables
def initialize_database(db_path=DB_PATH):

    connection = get_connection(db_path)

    cursor = connection.cursor()

    # Sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            transaction_id TEXT PRIMARY KEY,
            order_date TEXT,
            product TEXT,
            category TEXT,
            region TEXT,
            sales_channel TEXT,
            quantity INTEGER,
            unit_price REAL,
            discount_amount REAL,
            status TEXT
        )
    """)

    # Table to store data quality problems
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_quality_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            issue_description TEXT
        )
    """)

    connection.commit()

    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database and tables created successfully!")