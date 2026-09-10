from datetime import date
from io import BytesIO

from pypdf import PdfWriter

from backend.ai.extractor import ExtractedInvoice, ExtractedItem


def _blank_pdf() -> bytes:
    stream = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(stream)
    return stream.getvalue()


def test_upload_stores_document_metadata(client, auth_headers):
    response = client.post(
        "/documents",
        headers=auth_headers,
        files={"file": ("receipt.pdf", _blank_pdf(), "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["original_filename"] == "receipt.pdf"


def test_upload_rejects_unsupported_type(client, auth_headers):
    response = client.post(
        "/documents",
        headers=auth_headers,
        files={"file": ("receipt.txt", b"not allowed", "text/plain")},
    )
    assert response.status_code == 400


def test_receipt_requires_confirmation_before_creating_product(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.document_service._text", lambda _document: "invoice text")
    monkeypatch.setattr(
        "backend.services.document_service.extract_product_fields",
        lambda _text: ExtractedInvoice(
            seller="Laptop Store",
            purchase_date=date(2026, 1, 10),
            invoice_number="INV-2048",
            items=[
                ExtractedItem(
                    product_name="Lenovo Laptop",
                    brand="Lenovo",
                    price="75000.00",
                    serial_number="ABC123",
                    warranty_months=12,
                ),
                ExtractedItem(product_name="Logitech Mouse", brand="Logitech", price="2499.00"),
            ],
        ),
    )
    upload = client.post(
        "/documents",
        headers=auth_headers,
        files={"file": ("invoice.pdf", _blank_pdf(), "application/pdf")},
    )
    document_id = upload.json()["id"]

    preview = client.post(f"/documents/{document_id}/extract", headers=auth_headers)
    assert preview.status_code == 200
    assert preview.json()["requires_confirmation"] is True
    assert [item["product_name"] for item in preview.json()["items"]] == [
        "Lenovo Laptop",
        "Logitech Mouse",
    ]
    assert client.get("/products", headers=auth_headers).json()["total"] == 0

    confirmed = client.post(
        f"/documents/{document_id}/confirm",
        headers=auth_headers,
        json={
            "products": [
                {
                    "product_name": "Lenovo Laptop",
                    "brand": "Lenovo",
                    "seller": "Laptop Store",
                    "purchase_date": "2026-01-10",
                    "price": "75000.00",
                    "serial_number": "ABC123",
                    "warranty_months": 12,
                },
                {
                    "product_name": "Logitech Mouse",
                    "brand": "Logitech",
                    "seller": "Laptop Store",
                    "purchase_date": "2026-01-10",
                    "price": "2499.00",
                },
            ],
            "reminder_days": [30, 7],
        },
    )
    assert confirmed.status_code == 201
    products = confirmed.json()
    assert products[0]["warranty_expiry_date"] == "2027-01-10"
    assert client.get("/products", headers=auth_headers).json()["total"] == 2
    first_documents = client.get(
        f"/documents?product_id={products[0]['id']}", headers=auth_headers
    ).json()
    second_documents = client.get(
        f"/documents?product_id={products[1]['id']}", headers=auth_headers
    ).json()
    assert first_documents[0]["id"] == second_documents[0]["id"] == document_id


def test_documents_are_listed_and_downloaded_for_their_product(client, auth_headers):
    product = client.post(
        "/products",
        headers=auth_headers,
        json={"product_name": "Laptop"},
    ).json()
    uploaded = client.post(
        "/documents",
        headers=auth_headers,
        data={"product_id": product["id"]},
        files={"file": ("invoice.pdf", _blank_pdf(), "application/pdf")},
    )
    assert uploaded.status_code == 201

    documents = client.get(f"/documents?product_id={product['id']}", headers=auth_headers)
    assert documents.status_code == 200
    assert [document["original_filename"] for document in documents.json()] == ["invoice.pdf"]

    download = client.get(
        f"/documents/{uploaded.json()['id']}/download",
        headers=auth_headers,
    )
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"

    deleted = client.delete(f"/documents/{uploaded.json()['id']}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/documents?product_id={product['id']}", headers=auth_headers).json() == []
