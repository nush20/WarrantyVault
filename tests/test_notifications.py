from datetime import date, timedelta


def test_generate_and_read_warranty_reminder(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        "backend.services.reminder_service.send_warranty_reminder",
        lambda **_kwargs: None,
    )
    product = client.post(
        "/products",
        headers=auth_headers,
        json={
            "product_name": "Headphones",
            "purchase_date": date.today().isoformat(),
            "warranty_expiry_date": (date.today() + timedelta(days=1)).isoformat(),
        },
    )
    assert product.status_code == 201

    product_id = product.json()["id"]
    defaults = client.get(f"/products/{product_id}/reminders", headers=auth_headers)
    assert defaults.json()["days_before"] == [30, 7]

    preferences = client.put(
        f"/products/{product_id}/reminders",
        headers=auth_headers,
        json={"days_before": [30, 7, 1]},
    )
    assert preferences.status_code == 200
    assert preferences.json()["days_before"] == [30, 7, 1]

    generated = client.post("/notifications/generate", headers=auth_headers)
    assert generated.status_code == 200
    assert generated.json()["created"] == 1
    assert generated.json()["sent"] == 1
    assert generated.json()["failed"] == 0
    assert generated.json()["checked_at"] == date.today().isoformat()

    duplicate = client.post("/notifications/generate", headers=auth_headers)
    assert duplicate.json()["created"] == 0
    assert duplicate.json()["sent"] == 0

    notifications = client.get("/notifications?unread_only=true", headers=auth_headers).json()
    assert len(notifications) == 1
    assert {notification["product_id"] for notification in notifications} == {product_id}
    assert {notification["days_before"] for notification in notifications} == {1}
    assert {notification["status"] for notification in notifications} == {"sent"}
    assert {notification["attempt_count"] for notification in notifications} == {1}
    assert {notification["reminder_date"] for notification in notifications} == {
        date.today().isoformat()
    }

    marked = client.patch(f"/notifications/{notifications[0]['id']}/read", headers=auth_headers)
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True
