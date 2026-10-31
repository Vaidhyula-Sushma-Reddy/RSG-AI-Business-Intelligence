import sqlite3
import re
import time

from database import DB_PATH


# Maximum time allowed for a query
QUERY_TIMEOUT = 5

# Maximum number of rows returned
MAX_ROWS = 100


def validate_sql(sql):

    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    sql = sql.strip()

    # Remove one optional trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # Reject multiple statements and internal semicolons
    if ";" in sql:
        raise ValueError("Multiple SQL statements are not allowed.")

    # Only SELECT or WITH queries are allowed
    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject SQL comments
    if "--" in sql or "/*" in sql or "*/" in sql:
        raise ValueError("SQL comments are not allowed.")

    return sql


def execute_sql(sql):

    # Step 1: Validate the generated SQL
    sql = validate_sql(sql)

    # Step 2: Open database in read-only mode
    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
        timeout=QUERY_TIMEOUT
        
    )

    connection.row_factory = sqlite3.Row

    # Step 3: Allow only safe database operations
    allowed_actions = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_RECURSIVE
    }

    def authorize(action, arg1, arg2, database_name, trigger_name):

        if action not in allowed_actions:
            return sqlite3.SQLITE_DENY

        # Allow reading only from the sales table
        if action == sqlite3.SQLITE_READ:

            if arg1 != "sales":
                return sqlite3.SQLITE_DENY

        # Block dangerous functions
        if action == sqlite3.SQLITE_FUNCTION:

            function_name = (arg2 or "").lower()

            if function_name == "load_extension":
                return sqlite3.SQLITE_DENY

        return sqlite3.SQLITE_OK

    connection.set_authorizer(authorize)

    # Step 4: Set a query execution time limit
    start_time = time.monotonic()

    def stop_long_query():

        if time.monotonic() - start_time > QUERY_TIMEOUT:
            return 1

        return 0

    connection.set_progress_handler(stop_long_query, 1000)

    try:

        cursor = connection.cursor()

        # Step 5: Execute the query
        cursor.execute(sql)

        # Step 6: Fetch a limited number of rows
        rows = cursor.fetchmany(MAX_ROWS + 1)

        if len(rows) > MAX_ROWS:
            raise ValueError(
                f"Query returned too many rows. Maximum allowed: {MAX_ROWS}."
            )

        # Convert SQLite rows into normal dictionaries
        results = [
            dict(row)
            for row in rows
        ]

        return {
            "columns": [
                description[0]
                for description in cursor.description
            ],
            "rows": results
        }

    finally:

        connection.close()