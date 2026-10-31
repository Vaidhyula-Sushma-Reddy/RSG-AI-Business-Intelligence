# SalesLens – System Architecture

## 1. Overview

SalesLens is an AI-powered Business Intelligence application that allows users to ask questions about sales data using natural language.

The application converts user questions into SQL queries using the Groq AI API, executes permitted queries against an SQLite database, and presents the results in a suitable format.

## 2. Architecture Diagram

```text
                 USER
                   |
                   v
        FRONTEND (HTML, CSS, JS)
                   |
             POST /ask
                   |
                   v
            FLASK BACKEND
                app.py
                   |
                   v
             AI SERVICE
             ai_service.py
                   |
              GROQ API
                   |
          Generated SQL + JSON
                   |
                   v
             SQL EXECUTOR
            sql_executor.py
                   |
             SQL VALIDATION
                   |
                   v
             SQLITE DATABASE
              database.py
                   |
             QUERY RESULTS
                   |
                   v
          ANSWER GENERATION
                app.py
                   |
                   v
       ANSWER / TABLE / CHART
                   |
                   v
                USER
```

## 3. Main Components

### 3.1 Frontend

Files:
- `templates/index.html`
- `static/style.css`
- `static/script.js`

Responsibilities:
- Accept natural-language questions.
- Send requests to the Flask backend.
- Display answers and supporting data.
- Render charts using Chart.js.
- Display loading indicators and error messages.

### 3.2 Flask Backend

File: `app.py`

Responsibilities:
- Handle HTTP requests.
- Validate user questions.
- Coordinate AI interpretation and SQL execution.
- Generate human-readable answers.
- Return results to the frontend as JSON.

### 3.3 AI Service

File: `ai_service.py`

Responsibilities:
- Send the user's question to the Groq API.
- Provide the database schema and business rules to the AI model.
- Generate SQL and visualization instructions.
- Identify unsupported and unrelated questions.
- Return structured JSON.

### 3.4 SQL Executor

File: `sql_executor.py`

Responsibilities:
- Validate generated SQL queries.
- Allow permitted read-only SELECT and WITH queries.
- Restrict access to the sales table.
- Reject write operations and unsafe SQL.
- Execute valid queries against SQLite.
- Return columns and rows.

### 3.5 Database Layer

File: `database.py`

Responsibilities:
- Initialize the SQLite database.
- Create the sales table.
- Create the data quality issues table.
- Provide database connections.

### 3.6 Data Loader

File: `data_loader.py`

Responsibilities:
- Read sales records from `sales.csv`.
- Load records into SQLite.
- Identify missing or invalid data.
- Record data quality issues.

## 4. Data Flow

1. The user enters a question in the web interface.
2. JavaScript sends the question to the Flask `/ask` endpoint.
3. Flask validates the input.
4. The AI service sends the question and database instructions to Groq.
5. Groq returns structured JSON containing the generated SQL and visualization instructions.
6. The SQL executor validates the SQL query.
7. The validated query is executed against the SQLite database.
8. Flask prepares a human-readable answer and supporting data.
9. The frontend displays the answer as a metric, table, or chart.

## 5. Business Rules

Revenue is calculated as:

**Revenue = (Quantity × Unit Price) − Discount Amount**

Only completed transactions with valid quantity and price information are included in revenue calculations.

Missing values are not automatically treated as zero.

## 6. Security Considerations

The SQL executor applies restrictions to reduce the risk of unsafe database operations:

- Only permitted read-only queries are accepted.
- Access is restricted to the sales table.
- Write operations are rejected.
- Multiple SQL statements are rejected.
- SQL comments are rejected.
- Query results are limited.

The application also validates the user's question before sending it for AI processing.

## 7. Error Handling

SalesLens handles several error conditions:

- Empty or excessively long questions.
- Unsupported business questions.
- Questions unrelated to sales analytics.
- SQL execution errors.
- AI service rate limits.
- Missing API configuration.
- Unexpected application errors.

The application returns understandable error messages instead of exposing internal implementation details to users.
