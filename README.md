# WarrantyVault

WarrantyVault is a warranty-management application for keeping products, purchase details, receipts, warranty documents, and expiry reminders in one place. It provides a FastAPI backend, a PostgreSQL-compatible data model, JWT authentication, scheduled email reminders, optional Gemini invoice extraction, and a lightweight Streamlit interface.

## Features

- Secure signup and login with password hashing and JWT authentication
- Product CRUD with search, filters, pagination, and ownership protection
- Automatic warranty status and expiry tracking
- PDF/image storage with authenticated download and deletion
- Many-to-many product–document relationships for multi-item invoices
- Gemini-powered invoice prefill with editable review before saving
- Product-specific 30-day, 7-day, and 1-day email reminders
- Dashboard counts for active, expiring, and expired warranties

## Architecture

```text
Streamlit → FastAPI routers → service layer → SQLAlchemy → PostgreSQL
                                ├── local document storage
                                ├── Gemini extraction (optional)
                                └── daily reminder scheduler → SMTP
```

```text
backend/
├── ai/          # PDF text and invoice-field extraction
├── database/    # Engine and database sessions
├── models/      # SQLAlchemy tables
├── routers/     # HTTP endpoints
├── schemas/     # Pydantic request/response models
├── services/    # Business logic
├── utils/       # Auth dependencies and exceptions
└── main.py      # FastAPI application and scheduler startup
```

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn backend.main:app --reload
```

Swagger UI: <http://localhost:8000/docs>

Start the Streamlit interface in another terminal:

```bash
source .venv/bin/activate
python -m streamlit run streamlit_app.py
```

Application: <http://localhost:8501>

SQLite is used for simple local development. Set `DATABASE_URL` in `.env` to use PostgreSQL. Add `GEMINI_API_KEY` only for invoice prefill, and configure the `SMTP_*` variables to send reminder emails.

## Main workflow

```text
Add product manually ───────────────┐
                                    ├─→ Save product → Track expiry → Send reminders
Upload invoice → Extract → Review ──┘                    └─→ Attach claim documents
```

Invoice extraction never saves products automatically. The user reviews and edits detected items first. One invoice can then be linked to multiple products through the `product_documents` junction table.

## Key endpoints

| Endpoint | Purpose |
| --- | --- |
| `POST /auth/signup`, `POST /auth/login` | Account creation and JWT login |
| `GET`, `POST /products` | Filtered product listing and creation |
| `GET`, `PATCH`, `DELETE /products/{id}` | Product CRUD |
| `GET /products/expiring` | Warranties expiring within a given window |
| `POST /documents` | Upload a receipt or warranty document |
| `POST /documents/{id}/extract` | Generate an editable invoice preview |
| `POST /documents/{id}/confirm` | Save confirmed products and document links |
| `GET /analytics/summary` | Dashboard warranty counts |

## Tests

```bash
pytest -q
```

Tests cover authentication, user-scoped product CRUD, filtering, expiry calculation, document handling, invoice confirmation, analytics, and duplicate-safe reminders.

## Scope

- Text-based PDFs are supported; OCR for scanned PDFs/images is intentionally excluded.
- Files are stored locally while metadata is stored in SQL. Object storage is the natural production upgrade.
- The in-process scheduler is suitable for this project scope; a deployed multi-instance service should use one platform-scheduled job.
