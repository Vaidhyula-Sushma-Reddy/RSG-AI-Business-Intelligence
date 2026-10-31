import pytest
import app as sales_app


@pytest.fixture
def client():
    sales_app.app.config["TESTING"] = True

    with sales_app.app.test_client() as client:
        yield client


# 1. Test home page
def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200


# 2. Test health check
def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


# 3. Test empty question
def test_empty_question(client):
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data


# 4. Test missing question
def test_missing_question(client):
    response = client.post("/ask", json={})

    assert response.status_code == 400


# 5. Test question exceeding 300 characters
def test_long_question(client):
    response = client.post(
        "/ask",
        json={"question": "a" * 301}
    )

    assert response.status_code == 400


# 6. Test unsupported question
def test_unsupported_question(client, monkeypatch):

    monkeypatch.setattr(
        sales_app,
        "interpret_question",
        lambda question: {
            "status": "unsupported",
            "reason": "Profit data is unavailable"
        }
    )

    response = client.post(
        "/ask",
        json={"question": "What is the profit?"}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "unsupported"
    assert "profitability" in data["error"].lower()


# 7. Test successful metric question
def test_successful_revenue_question(client, monkeypatch):

    monkeypatch.setattr(
        sales_app,
        "interpret_question",
        lambda question: {
            "status": "ok",
            "sql": "SELECT SUM(100) AS total_revenue",
            "visualization": {
                "type": "metric",
                "title": "Total Revenue",
                "x_axis": "",
                "y_axis": ""
            }
        }
    )

    monkeypatch.setattr(
        sales_app,
        "execute_sql",
        lambda sql: {
            "columns": ["total_revenue"],
            "rows": [(100,)]
        }
    )

    response = client.post(
        "/ask",
        json={"question": "What is the total revenue?"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert "₹100" in data["answer"]
    assert data["supporting_data"]["rows"] == [[100]]


# 8. Test question unrelated to sales
def test_out_of_scope_question(client, monkeypatch):

    monkeypatch.setattr(
        sales_app,
        "interpret_question",
        lambda question: {
            "status": "out_of_scope"
        }
    )

    response = client.post(
        "/ask",
        json={"question": "Tell me a joke"}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "out_of_scope"


# 9. Test SQL execution error
def test_sql_error(client, monkeypatch):

    monkeypatch.setattr(
        sales_app,
        "interpret_question",
        lambda question: {
            "status": "ok",
            "sql": "SELECT * FROM sales",
            "visualization": {"type": "table"}
        }
    )

    def raise_sql_error(sql):
        raise ValueError("Invalid SQL query")

    monkeypatch.setattr(
        sales_app,
        "execute_sql",
        raise_sql_error
    )

    response = client.post(
        "/ask",
        json={"question": "Show sales records"}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "query_error"


# 10. Test Groq rate limit error
def test_groq_rate_limit(client, monkeypatch):

    def raise_rate_limit(question):
        raise Exception("429 Too Many Requests")

    monkeypatch.setattr(
        sales_app,
        "interpret_question",
        raise_rate_limit
    )

    response = client.post(
        "/ask",
        json={"question": "What is the total revenue?"}
    )

    assert response.status_code == 503

    data = response.get_json()

    assert data["status"] == "service_error"
