let currentChart = null;


// Fill the input box when an example question is clicked
function useQuestion(question) {
    document.getElementById("question").value = question;
}


// Allow users to submit by pressing Enter
document.getElementById("question").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        askQuestion();
    }
});


// Main function to ask a question
async function askQuestion() {

    const questionInput = document.getElementById("question");
    const askButton = document.getElementById("askButton");
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");

    const question = questionInput.value.trim();

    if (!question) {
        resultDiv.textContent = "Please enter a question.";
        return;
    }

    // Clear previous chart
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }

    // Hide previous SQL
    document.getElementById("sqlSection").style.display = "none";

    // Show loading
    loadingDiv.style.display = "block";
    askButton.disabled = true;
    askButton.textContent = "Processing...";

    resultDiv.replaceChildren();

    try {

        const response = await fetch("/ask", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        loadingDiv.style.display = "none";

        if (!response.ok) {
            showError(data.error || data.answer || "Something went wrong.");
            return;
        }

        // Display the answer
        displayAnswer(data);

        // Display supporting data
        if (data.supporting_data) {
            displaySupportingData(
                data.supporting_data,
                data.visualization
            );
        }

        // Display generated SQL
        if (data.generated_sql) {
            displaySQL(data.generated_sql);
        }

    } catch (error) {

        loadingDiv.style.display = "none";

        showError("Unable to connect to the backend. Please try again.");

        console.error("Error:", error);

    } finally {

        askButton.disabled = false;
        askButton.textContent = "Ask Question";
    }
}


// Display the main answer
function displayAnswer(data) {

    const resultDiv = document.getElementById("result");

    const heading = document.createElement("h2");
    heading.textContent = "Answer";

    const answer = document.createElement("p");
    answer.className = "answer-text";
    answer.textContent = data.answer || "Your query was processed successfully.";

    resultDiv.appendChild(heading);
    resultDiv.appendChild(answer);
}


// Display database results
function displaySupportingData(supportingData, visualization) {

    const resultDiv = document.getElementById("result");

    const columns = supportingData.columns || [];
    const rows = supportingData.rows || [];

    if (rows.length === 0) {

        const message = document.createElement("p");
        message.textContent = "No matching records found.";

        resultDiv.appendChild(message);
        return;
    }

    // Show a KPI card for a single numerical result
    if (
        rows.length === 1 &&
        columns.length === 1 &&
        isNumeric(getValue(rows[0], columns[0])) &&
        (!visualization || visualization.type === "metric" || visualization.type === "none")
    ) {

        displayMetric(columns[0], getValue(rows[0], columns[0]));
        return;
    }

    // Display a chart if the backend requests one
    if (
        visualization &&
        ["bar", "line", "pie"].includes(visualization.type)
    ) {

        displayChart(columns, rows, visualization);
        return;
    }

    // Otherwise display a table
    displayTable(columns, rows);
}


// Display a KPI card
function displayMetric(label, value) {

    const resultDiv = document.getElementById("result");

    const card = document.createElement("div");
    card.className = "metric-card";

    const metricLabel = document.createElement("p");
    metricLabel.className = "metric-label";
    metricLabel.textContent = formatLabel(label);

    const metricValue = document.createElement("h2");
    metricValue.className = "metric-value";
    metricValue.textContent = formatNumber(value);

    card.appendChild(metricLabel);
    card.appendChild(metricValue);

    resultDiv.appendChild(card);
}


// Display a table
function displayTable(columns, rows) {

    const resultDiv = document.getElementById("result");

    const heading = document.createElement("h3");
    heading.textContent = "Supporting Data";

    const tableContainer = document.createElement("div");
    tableContainer.className = "table-container";

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach(column => {

        const th = document.createElement("th");
        th.textContent = formatLabel(column);

        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    rows.forEach(row => {

        const tr = document.createElement("tr");

        columns.forEach(column => {

            const td = document.createElement("td");
            const value = getValue(row, column);

            td.textContent = value === null || value === undefined
                ? "—"
                : formatNumber(value);

            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    tbody.appendChild(document.createDocumentFragment());

    table.appendChild(tbody);
    tableContainer.appendChild(table);

    resultDiv.appendChild(heading);
    resultDiv.appendChild(tableContainer);
}


// Display a chart
function displayChart(columns, rows, visualization) {

    const resultDiv = document.getElementById("result");

    const chartHeading = document.createElement("h3");
    chartHeading.textContent = visualization.title || "Data Visualization";

    const chartContainer = document.createElement("div");
    chartContainer.className = "chart-container";

    const canvas = document.createElement("canvas");
    canvas.id = "resultChart";

    chartContainer.appendChild(canvas);

    resultDiv.appendChild(chartHeading);
    resultDiv.appendChild(chartContainer);

    const xAxis = visualization.x_axis || columns[0];
    const yAxis = visualization.y_axis || columns[1];

    const labels = rows.map(row => getValue(row, xAxis));

    const values = rows.map(row => Number(getValue(row, yAxis)));

    if (
        labels.some(value => value === null || value === undefined) ||
        values.some(value => !Number.isFinite(value))
    ) {
        displayTable(columns, rows);
        return;
    }

    const chartType = visualization.type;

    currentChart = new Chart(canvas, {

        type: chartType,

        data: {
            labels: labels,

            datasets: [{
                label: formatLabel(yAxis),
                data: values,
                borderWidth: 2,
                tension: 0.3
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: chartType === "pie"
                }
            },

            scales: chartType === "pie" ? {} : {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

}


// Display generated SQL
function displaySQL(sql) {

    const sqlSection = document.getElementById("sqlSection");
    const sqlQuery = document.getElementById("sqlQuery");

    sqlQuery.textContent = sql;

    sqlSection.style.display = "block";
}


// Display errors
function showError(message) {

    const resultDiv = document.getElementById("result");

    resultDiv.replaceChildren();

    const heading = document.createElement("h2");
    heading.textContent = "Unable to answer";

    const errorMessage = document.createElement("p");
    errorMessage.textContent = message;

    resultDiv.appendChild(heading);
    resultDiv.appendChild(errorMessage);
}


// Get a value from a database row
function getValue(row, column) {

    if (Array.isArray(row)) {
        const columns = row;
        return columns[column];
    }

    return row[column];
}


// Check whether a value is numeric
function isNumeric(value) {

    return value !== null &&
           value !== undefined &&
           value !== "" &&
           Number.isFinite(Number(value));
}


// Format numbers
function formatNumber(value) {

    if (isNumeric(value)) {

        return Number(value).toLocaleString("en-IN", {
            maximumFractionDigits: 2
        });
    }

    return value;
}


// Convert database column names into readable labels
function formatLabel(label) {

    return String(label)
        .replace(/_/g, " ")
        .replace(/\b\w/g, character => character.toUpperCase());
}