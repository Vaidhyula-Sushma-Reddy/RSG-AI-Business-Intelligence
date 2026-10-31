# SalesLens – AI Development Report

## 1. AI Tools Used

The following AI tools were used during the development of SalesLens:

- **ChatGPT:** Used as a development assistant for understanding requirements, designing the application structure, generating code suggestions, debugging errors, and improving the application.
- **Groq API (openai/gpt-oss-120b):** Integrated into the application to interpret natural-language business questions and generate SQL queries along with visualization instructions.

## 2. How AI Was Used During Development

AI assistance was used throughout different stages of development.

### Requirement Understanding
- Used AI assistance to break down the business intelligence requirements.
- Identified the main application components and their responsibilities.
- Planned the flow from natural-language questions to database results.

### Application Development
- Used AI assistance for implementing Flask routes and backend logic.
- Developed the AI service for natural-language-to-SQL generation.
- Improved the SQL execution process with read-only query restrictions.
- Built the frontend to display answers, tables, and charts.

### Debugging and Improvement
- Used AI assistance to understand Python errors and API responses.
- Improved error handling for unsupported questions and invalid inputs.
- Refined the application responses to make them more understandable.
- Added automated backend tests using pytest.

## 3. Problems Encountered

### AI API Limitations
The initial Gemini integration encountered free-tier request quota limitations.

**Solution:** Switched to the Groq API and configured a supported model for natural-language question processing.

### Model Availability Error
An initially selected Groq model returned a model-not-found error.

**Solution:** Changed the model configuration to `openai/gpt-oss-120b`.

### SQL Query Handling
Some questions could produce empty or NULL database results, especially when users requested months outside the available dataset period.

**Solution:** Added handling for empty results and NULL aggregate values, with user-friendly messages.

### Frontend Styling and Backend Connectivity
During development, changes to frontend styling were not immediately visible, and backend connectivity needed verification.

**Solution:** Checked the Flask application, used the health-check endpoint, and refreshed the browser cache when verifying styling changes.

### Port Conflict
The default Flask port was already occupied.

**Solution:** Changed the application port to 5001.

## 4. Testing and Debugging

Automated backend tests were implemented using pytest.

The test suite covers:

- Home page availability.
- Backend health check.
- Empty and missing questions.
- Maximum question length validation.
- Unsupported business questions.
- Successful revenue requests.
- Out-of-scope questions.
- SQL execution errors.
- AI service rate-limit errors.

The current test execution result was:

**10 tests passed successfully.**

Mocking was used to simulate AI responses and SQL execution in the tests, avoiding unnecessary external API calls.

## 5. What I Would Improve With One Additional Day

If given one additional day, I would focus on:

1. Improving natural-language-to-SQL accuracy for complex business questions.
2. Adding more test cases for SQL security and data quality.
3. Improving chart selection and visualization accuracy.
4. Adding more meaningful business insights and comparisons.
5. Improving frontend responsiveness and user experience.
6. Adding integration tests using the actual database.
7. Improving documentation and deployment readiness.

## 6. Conclusion

Developing SalesLens provided practical experience in integrating generative AI with a business intelligence application.

The project combines natural-language processing, SQL query generation, database operations, backend development, frontend visualization, and automated testing.

AI tools were used as development assistance, while the application logic, integrations, testing, and debugging were carried out as part of the project development process.
