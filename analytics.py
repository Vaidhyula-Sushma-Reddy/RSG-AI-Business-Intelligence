from database import get_connection


def get_total_revenue():

    connection = get_connection()

    result = connection.execute("""
        SELECT SUM((quantity * unit_price) - discount_amount)
        AS total_revenue
        FROM sales
        WHERE status = 'Completed'
        AND quantity > 0
        AND unit_price IS NOT NULL
        AND discount_amount IS NOT NULL
    """).fetchone()

    connection.close()

    return result["total_revenue"] or 0


def get_top_product():

    connection = get_connection()

    result = connection.execute("""
        SELECT
            product,
            SUM((quantity * unit_price) - discount_amount)
            AS revenue
        FROM sales
        WHERE status = 'Completed'
        AND quantity > 0
        AND unit_price IS NOT NULL
        AND discount_amount IS NOT NULL
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 1
    """).fetchone()

    connection.close()

    if result is None:
        return None

    return dict(result)


def get_monthly_revenue():

    connection = get_connection()

    results = connection.execute("""
        SELECT
            substr(order_date, 1, 7) AS month,
            SUM((quantity * unit_price) - discount_amount)
            AS revenue
        FROM sales
        WHERE status = 'Completed'
        AND quantity > 0
        AND unit_price IS NOT NULL
        AND discount_amount IS NOT NULL
        GROUP BY substr(order_date, 1, 7)
        ORDER BY month
    """).fetchall()

    connection.close()

    return [dict(row) for row in results]


def get_top_region():

    connection = get_connection()

    result = connection.execute("""
        SELECT
            region,
            SUM((quantity * unit_price) - discount_amount)
            AS revenue
        FROM sales
        WHERE status = 'Completed'
        AND quantity > 0
        AND unit_price IS NOT NULL
        AND discount_amount IS NOT NULL
        GROUP BY region
        ORDER BY revenue DESC
        LIMIT 1
    """).fetchone()

    connection.close()

    if result is None:
        return None

    return dict(result)


def compare_months(month1, month2):

    connection = get_connection()

    query = """
        SELECT
            substr(order_date, 1, 7) AS month,
            SUM((quantity * unit_price) - discount_amount)
            AS revenue
        FROM sales
        WHERE status = 'Completed'
        AND quantity > 0
        AND unit_price IS NOT NULL
        AND discount_amount IS NOT NULL
        AND substr(order_date, 1, 7) IN (?, ?)
        GROUP BY substr(order_date, 1, 7)
    """

    results = connection.execute(
        query, (month1, month2)
    ).fetchall()

    connection.close()

    revenue_by_month = {
        row["month"]: row["revenue"]
        for row in results
    }

    revenue1 = revenue_by_month.get(month1, 0) or 0
    revenue2 = revenue_by_month.get(month2, 0) or 0

    difference = revenue2 - revenue1

    return {
        "month1": month1,
        "revenue1": revenue1,
        "month2": month2,
        "revenue2": revenue2,
        "difference": difference
    }


if __name__ == "__main__":

    print("Total Revenue:", get_total_revenue())

    print("\nTop Product:", get_top_product())

    print("\nMonthly Revenue:", get_monthly_revenue())

    print("\nTop Region:", get_top_region())

    print("\nCompare January and February:")
    print(compare_months("2026-01", "2026-02"))