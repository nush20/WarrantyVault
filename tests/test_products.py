from datetime import date


def test_product_crud_calculates_expiry(client, auth_headers):
    payload = {
        "product_name": "Laptop",
        "category": "Electronics",
        "brand": "Framework",
        "purchase_date": "2024-01-31",
        "price": "1200.00",
        "warranty_months": 1,
        "invoice_number": "INV-101",
        "warranty_provider": "Framework",
        "support_email": "support@example.com",
    }
    created = client.post("/products", json=payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["warranty_expiry_date"] == "2024-02-29"
    assert created.json()["invoice_number"] == "INV-101"
    product_id = created.json()["id"]

    fetched = client.get(f"/products/{product_id}", headers=auth_headers)
    assert fetched.json()["product_name"] == "Laptop"

    updated = client.patch(f"/products/{product_id}", json={"warranty_months": 24}, headers=auth_headers)
    assert updated.json()["warranty_expiry_date"] == "2026-01-31"

    assert client.delete(f"/products/{product_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/products/{product_id}", headers=auth_headers).status_code == 404


def test_filters_pagination_and_analytics(client, auth_headers):
    products = [
        {
            "product_name": "Phone",
            "category": "Electronics",
            "brand": "Acme",
            "purchase_date": date.today().isoformat(),
            "price": "500.00",
            "warranty_months": 12,
        },
        {"product_name": "Chair", "category": "Furniture", "brand": "SeatCo", "price": "200.00"},
    ]
    for product in products:
        assert client.post("/products", json=product, headers=auth_headers).status_code == 201

    page = client.get("/products?page=1&page_size=1", headers=auth_headers).json()
    assert page["total"] == 2 and page["pages"] == 2 and len(page["items"]) == 1
    filtered = client.get("/products?brand=acme&warranty_status=active", headers=auth_headers).json()
    assert filtered["total"] == 1

    analytics = client.get("/analytics/summary?expiring_within_days=30", headers=auth_headers)
    assert analytics.status_code == 200
    result = analytics.json()
    assert result["total_products"] == 2
    assert result["active_warranties"] == 1
    assert result["expired_warranties"] == 0
    assert "purchase_value_by_category" not in result
