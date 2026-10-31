# SalesLens – AI Business Intelligence Assistant

SalesLens is an AI-powered business intelligence application that allows users to analyze sales data using natural language.

Instead of writing SQL queries manually, users can ask questions in simple English. The application uses an AI model to understand the question, generate an SQL query, and return meaningful results.

Depending on the question, SalesLens presents the results as a numerical answer, a table, or a chart.

## Features

- Ask sales-related questions using natural language.
- Generate SQL queries using Groq AI.
- Analyze revenue, products, categories, regions, and sales channels.
- Display numerical results, tables, and charts.
- Handle unsupported and unrelated questions with friendly messages.
- Validate user input.
- Execute only permitted read-only SQL queries.
- Track data quality issues.
- Provide automated backend tests using pytest.

## Technologies Used

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| AI Integration | Groq API |
| AI Model | openai/gpt-oss-120b |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Testing | Pytest |

## Project Architecture

The application follows a simple layered architecture:

1. **Frontend:** Accepts questions and displays answers, tables, and charts.
2. **Flask Backend:** Receives requests and coordinates the application.
3. **AI Service:** Uses Groq to convert natural-language questions into SQL and visualization instructions.
4. **SQL Executor:** Validates and executes permitted read-only SQL queries.
5. **SQLite Database:** Stores sales records and data quality information.
6. **Data Loader:** Imports sales data from the CSV file into SQLite.

### Application Flow

User Question  
↓  
Frontend (HTML, CSS, JavaScript)  
↓  
Flask Backend  
↓  
Groq AI Service  
↓  
SQL Query and Visualization Instructions  
↓  
SQL Validation and Execution  
↓  
SQLite Database  
↓  
Answer / Table / Chart  
↓  
Frontend Display

## Dataset and Business Rules

The application uses `sales.csv` as its input dataset.

The dataset contains information such as:

- Transaction ID
- Order date
- Product
- Category
- Region
- Sales channel
- Quantity
- Unit price
- Discount amount
- Transaction status

### Revenue Calculation

Revenue is calculated using:

Revenue = (Quantity × Unit Price) − Discount Amount

Only completed transactions with valid quantity and price information are included in revenue calculations. Missing values are not automatically treated as zero.

The application also records data quality issues for further inspection.

## Project Structure

```text
RSG-AI-Business-Intelligence/
│
├── app.py
├── ai_service.py
├── analytics.py
├── database.py
├── data_loader.py
├── sql_executor.py
│
├── sales.csv
├── requirements.txt
├── .env.example
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── tests/
│   ├── __init__.py
│   └── test_app.py
│
└── docs/
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd RSG-AI-Business-Intelligence
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

For Ubuntu/Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Groq API key

Create a `.env` file in the project root directory.

Add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not share or commit your actual API key.

### 6. Run the application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5001
```

The application initializes the database and loads the CSV data when necessary.

## Example Questions

Users can ask questions such as:

- What is the total revenue?
- Which product generated the highest revenue?
- Show monthly revenue trends.
- Compare revenue between January and February.
- Which region generated the highest revenue?
- Show revenue by sales channel.
- Display the top five products by revenue.
- How many completed transactions are there?

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Displays the SalesLens interface |
| GET | `/health` | Checks backend availability |
| POST | `/ask` | Processes a natural-language sales question |

Example request:

```json
{
  "question": "What is the total revenue?"
}
```

## Security and Validation

SalesLens includes basic safeguards for SQL execution:

- Allows only read-only SELECT and WITH queries.
- Restricts queries to the permitted sales table.
- Rejects SQL write operations.
- Rejects multiple SQL statements and SQL comments.
- Limits the maximum number of returned records.
- Uses a read-only database connection for query execution.

User input is also validated before processing.

## Automated Testing

The project uses pytest for automated backend testing.

Run the tests:

```bash
pytest -v
```

The current test suite contains 10 test cases covering:

- Home page availability
- Backend health check
- Empty and missing questions
- Questions exceeding the character limit
- Unsupported questions
- Successful revenue requests
- Out-of-scope questions
- SQL execution errors
- Groq API rate-limit errors

**Current test result:** 10 passed.

## Known Limitations

- The application analyzes only the information available in the supplied sales dataset.
- Customer-level analysis is unavailable because customer information is not provided.
- Profit and margin analysis are unavailable because product cost information is missing.
- Employee performance and inventory analysis are not supported.
- Forecasting future sales is not currently implemented.
- AI-generated SQL may require further refinement for complex questions.
- Groq API availability and request limits can affect response generation.

## Future Improvements

- Add support for larger datasets.
- Improve natural-language question understanding.
- Add more advanced business visualizations.
- Implement sales forecasting.
- Introduce user authentication.
- Add more automated integration and security tests.
- Improve query accuracy and error handling.

## Author

Developed as an AI Business Intelligence project for the RSG Research Private Limited Graduate Engineer Trainee assessment.

## Troubleshooting

If the application does not respond correctly, displays an error, or shows outdated content:

1. Make sure the Flask backend is running.
2. Open the application in your browser.
3. Press **Ctrl + Shift + R** to perform a hard refresh.
4. Try submitting your question again.

A hard refresh reloads the page and its static files, including JavaScript and CSS, from the server.

If the issue continues, check the terminal for backend errors and verify your Groq API key configuration.
