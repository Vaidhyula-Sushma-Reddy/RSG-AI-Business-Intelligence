import sqlite3

from flask import Flask, request, jsonify, render_template

from database import initialize_database, get_connection
from data_loader import load_sales_data

from ai_service import interpret_question
from sql_executor import execute_sql


app = Flask(__name__)


# =========================================
# 1. DATABASE INITIALIZATION
# =========================================

def setup_database():

    initialize_database()

    connection = get_connection()

    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

    finally:
        connection.close()

    if count == 0:
        load_sales_data()


setup_database()


# =========================================
# 2. HOME PAGE
# =========================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================
# 3. HEALTH CHECK
# =========================================

@app.route("/health")
def health():

    return jsonify({
        "status": "success",
        "message": "SalesLens is running successfully."
    }), 200


# =========================================
# 4. GET VALUE FROM DATABASE ROW
# =========================================

def get_row_value(row, column, index):

    if isinstance(row, dict):
        return row.get(column)

    if isinstance(row, (list, tuple)):
        return row[index]

    return None


# =========================================
# 5. FORMAT NUMBERS
# =========================================

def format_number(value):

    if isinstance(value, (int, float)):

        return f"{value:,.2f}".rstrip("0").rstrip(".")

    return str(value)


# =========================================
# 6. FRIENDLY ERROR MESSAGES
# =========================================

def get_friendly_error(question, reason=""):

    question_lower = question.lower()
    reason_lower = reason.lower()

    # Profit and cost questions
    if any(word in question_lower for word in [
        "profit", "cost", "margin", "expense"
    ]):

        return (
            "Profitability analysis is not available yet because "
            "the dataset does not contain product cost or expense data. "
            "You can still explore revenue, top products, categories, "
            "regions, and sales channels."
        )

    # Customer-related questions
    if any(word in question_lower for word in [
        "customer", "client", "buyer"
    ]):

        return (
            "Customer-level analysis is not available because "
            "customer information is not included in the current dataset. "
            "Try exploring product, category, or regional sales instead."
        )

    # Employee-related questions
    if any(word in question_lower for word in [
        "employee", "staff", "salesperson"
    ]):

        return (
            "Employee performance cannot be analyzed because "
            "the dataset does not contain employee information. "
            "You can explore sales by product, region, or sales channel."
        )

    # Inventory-related questions
    if any(word in question_lower for word in [
        "inventory", "stock level", "warehouse"
    ]):

        return (
            "Inventory analysis is unavailable because the dataset "
            "does not contain stock or warehouse information. "
            "You can explore product sales and revenue instead."
        )

    # Customer satisfaction questions
    if any(word in question_lower for word in [
        "satisfaction", "rating", "feedback", "review"
    ]):

        return (
            "Customer satisfaction cannot be measured because "
            "the dataset does not contain ratings or feedback. "
            "Try asking about sales performance instead."
        )

    # Forecasting questions
    if any(word in question_lower for word in [
        "forecast", "predict", "prediction", "future sales"
    ]):

        return (
            "Future sales forecasting is not currently supported. "
            "The available dataset contains historical sales from "
            "January to June 2026. You can explore historical monthly trends."
        )

    # General unsupported question
    return (
        "I couldn't answer this question using the available sales data. "
        "Try asking about total revenue, products, categories, regions, "
        "sales channels, or monthly sales trends."
    )


# =========================================
# 7. CREATE HUMAN-READABLE ANSWER
# =========================================

def create_answer(question, columns, rows, visualization):

    # No database records
    if not rows:

        return (
            "No matching sales records were found. "
            "Try changing the date, product, category, or region "
            "in your question."
        )

    # Check for NULL aggregate results
    if len(rows) == 1:

        values = [
            get_row_value(rows[0], column, index)
            for index, column in enumerate(columns)
        ]

        if values and all(value is None for value in values):

            question_lower = question.lower()

            requested_months = [
                "july", "august", "september",
                "october", "november", "december"
            ]

            if any(
                month in question_lower
                for month in requested_months
            ):

                return (
                    "No sales data is available for the requested month. "
                    "The current dataset covers January to June 2026."
                )

            return (
                "No matching sales records were found for this question. "
                "Please try different filters or another question."
            )

    visualization_type = visualization.get(
        "type", "table"
    )

    # Single numerical result
    if (
        visualization_type == "metric"
        and len(rows) == 1
        and len(columns) == 1
    ):

        value = get_row_value(
            rows[0],
            columns[0],
            0
        )

        if isinstance(value, (int, float)):

            label = columns[0].replace("_", " ")

            formatted_value = format_number(value)

            if "revenue" in label.lower():

                return (
                    f"The total revenue is ₹{formatted_value}."
                )

            return (
                f"The {label} is {formatted_value}."
            )

    # Chart answer
    if visualization_type in ["bar", "line", "pie"]:

        title = visualization.get(
            "title", "Sales Analysis"
        )

        return (
            f"Here is the {title.lower()} based on "
            "your actual sales database records."
        )

    # Table answer
    return (
        f"Found {len(rows)} matching record(s) "
        "for your question. Here are the results."
    )


# =========================================
# 8. ASK BUSINESS INTELLIGENCE QUESTION
# =========================================

@app.route("/ask", methods=["POST"])
def ask_question():

    try:

        # STEP 1: Receive user question
        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error": "Please send a valid question."
            }), 400

        question = data.get("question")

        # Empty question validation
        if not isinstance(question, str) or not question.strip():

            return jsonify({
                "error": (
                    "Please enter a question before clicking "
                    "the Get Answer button."
                )
            }), 400

        question = question.strip()

        # Question length validation
        if len(question) > 300:

            return jsonify({
                "error": (
                    "Your question is too long. "
                    "Please keep it within 300 characters."
                )
            }), 400

        # STEP 2: Understand question using Groq AI
        interpretation = interpret_question(question)

        status = interpretation["status"]

        # STEP 3: Handle unrelated questions
        if status == "out_of_scope":

            return jsonify({

                "status": "out_of_scope",

                "error": (
                    "I'm your Sales Analytics Assistant. "
                    "I can help you understand your sales data "
                    "through answers, tables, and charts. "
                    "Try asking about revenue, products, categories, "
                    "regions, or monthly sales."
                )

            }), 400

        # STEP 4: Handle unsupported questions
        if status == "unsupported":

            reason = interpretation.get(
                "reason", ""
            )

            return jsonify({

                "status": "unsupported",

                "error": get_friendly_error(
                    question,
                    reason
                )

            }), 400

        # STEP 5: Get generated SQL
        sql = interpretation.get("sql", "")

        if not sql:

            return jsonify({

                "status": "error",

                "error": (
                    "I couldn't prepare an analysis for this question. "
                    "Please try asking in a different way."
                )

            }), 400

        # STEP 6: Get visualization instructions
        visualization = interpretation.get(
            "visualization",
            {
                "type": "table",
                "title": "Sales Analysis",
                "x_axis": "",
                "y_axis": ""
            }
        )

        # STEP 7: Execute SQL safely
        query_result = execute_sql(sql)

        rows = query_result["rows"]

        columns = query_result["columns"]

        # STEP 8: Generate readable answer
        answer = create_answer(
            question,
            columns,
            rows,
            visualization
        )

        # STEP 9: Return results to frontend
        return jsonify({

            "status": "success",

            "answer": answer,

            "supporting_data": {

                "columns": columns,

                "rows": rows

            },

            "visualization": visualization,

            "generated_sql": sql

        }), 200

    except Exception as error:

        app.logger.exception(
            "Error processing business analytics question"
        )

        error_message = str(error).upper()

        # STEP 10: Handle Groq rate limits
        if (
            "429" in error_message
            or "RATE_LIMIT" in error_message
            or "TOO MANY REQUESTS" in error_message
        ):

            return jsonify({

                "status": "service_error",

                "error": (
                    "The AI service is temporarily busy "
                    "because its request limit has been reached. "
                    "Please try again later."
                )

            }), 503

        # STEP 11: Handle missing API key
        if (
            "GROQ_API_KEY" in error_message
            or "API KEY IS MISSING" in error_message
        ):

            return jsonify({

                "status": "service_error",

                "error": (
                    "The AI service is not configured correctly. "
                    "Please check the application configuration."
                )

            }), 503

        # STEP 12: Handle SQL errors
        if isinstance(error, (ValueError, sqlite3.Error)):

            return jsonify({

                "status": "query_error",

                "error": (
                    "I couldn't complete this analysis. "
                    "Please rephrase your question and try again."
                )

            }), 400

        # STEP 13: Handle unexpected errors
        return jsonify({

            "status": "error",

            "error": (
                "Something unexpected happened while processing "
                "your question. Please try again."
            )

        }), 500


# =========================================
# 9. RUN FLASK APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )