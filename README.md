# WarrantyVault

**WarrantyVault** is a warranty-management application for storing products, receipts, and warranty documents while **tracking warranty expirations and sending reminders before coverage ends**.

It combines a **FastAPI backend, JWT authentication, relational data modelling, scheduled email reminders, optional Gemini-assisted invoice extraction, and a Streamlit interface**.

## Features

* 🔐 **JWT Authentication & Authorization** — Secure signup/login with password hashing and user-scoped access.
* 📦 **Product Management** — CRUD operations with search, filtering, pagination, ownership protection, and automatic warranty-expiry calculation.
* 📄 **Document Management** — Authenticated upload, download, and deletion of PDF/image warranty documents.
* 🔗 **Many-to-Many Relationships** — A single invoice can be linked to multiple products, while each product can have multiple documents.
* ✨ **Invoice Autofill** — Gemini converts text-based invoice PDFs into structured product information, with **editable user review before database writes**.
* 🔔 **Warranty Reminders** — Configurable **30-day, 7-day, and 1-day** expiry reminders delivered through email.
* 🛡️ **Duplicate-Safe Notifications** — Database-backed notification records prevent repeated reminders for the same product and reminder type.
* 📊 **Dashboard Analytics** — SQL-based counts for active, expiring, and expired warranties.

## Architecture

```text
Streamlit → FastAPI routers → Service layer → SQLAlchemy → PostgreSQL
                                ├── Local document storage
                                ├── Gemini extraction (optional)
                                └── Daily reminder scheduler → SMTP
```

The backend follows a **layered architecture**, keeping HTTP handling, validation, business logic, and persistence separate.

```text
backend/
├── ai/          # PDF text and invoice-field extraction
├── database/    # Engine and database sessions
├── models/      # SQLAlchemy tables
├── routers/     # FastAPI endpoints
├── schemas/     # Pydantic request/response models
├── services/    # Business logic
├── utils/       # Authentication and exceptions
└── main.py      # Application entry point and scheduler startup
```

## Main Workflow

```text
Add product manually ───────────────┐
                                    ├──→ Save product
Upload invoice → Extract → Review ──┘        ↓
                                      Track expiry
                                            ↓
                                     Schedule reminder
                                            ↓
                                         Email
```

Invoice extraction **never automatically modifies product data**.

```text
Invoice
   ↓
Extract text
   ↓
Gemini structured extraction
   ↓
Pydantic validation
   ↓
Editable preview
   ↓
User confirmation
   ↓
Create products + link invoice
```

This keeps AI-assisted input separate from authoritative application data.

## Key Endpoints

| Endpoint                          | Purpose                                     |
| --------------------------------- | ------------------------------------------- |
| `POST /auth/signup`               | Create an account                           |
| `POST /auth/login`                | Authenticate and receive JWT                |
| `GET /products`                   | Search, filter and paginate products        |
| `POST /products`                  | Create product                              |
| `GET/PATCH/DELETE /products/{id}` | Product CRUD                                |
| `GET /products/expiring`          | Find warranties expiring within a window    |
| `POST /documents`                 | Upload receipt/warranty document            |
| `POST /documents/{id}/extract`    | Generate editable invoice preview           |
| `POST /documents/{id}/confirm`    | Confirm products and document relationships |
| `GET /analytics/summary`          | Retrieve dashboard warranty statistics      |

Protected operations are **scoped to the authenticated user**, preventing users from accessing another account's products or documents.

## Tech Stack

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy
**Database:** PostgreSQL / SQLite
**Authentication:** JWT + password hashing
**AI:** Google Gemini
**Frontend:** Streamlit
**Notifications:** Scheduled jobs + SMTP

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python -m uvicorn backend.main:app --reload
```

FastAPI Swagger UI:

```text
http://localhost:8000/docs
```

Start Streamlit in another terminal:

```bash
source .venv/bin/activate
python -m streamlit run streamlit_app.py
```

Application:

```text
http://localhost:8501
```

SQLite is used for simple local development. Set `DATABASE_URL` in `.env` to use PostgreSQL.

`GEMINI_API_KEY` is required only for invoice prefill. Configure the `SMTP_*` variables to enable reminder emails.

## Tests

```bash
pytest -q
```

Tests cover:

* Authentication and authorization
* User-scoped product CRUD
* Search, filtering, and pagination
* Warranty-expiry calculations
* Document handling
* Invoice confirmation
* Dashboard analytics
* Duplicate-safe reminder processing

