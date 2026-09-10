# WarrantyVault

WarrantyVault is a warranty management application for storing products and purchase documents, tracking warranty expirations, and sending configurable email reminders.

It uses **FastAPI, SQLAlchemy, PostgreSQL, JWT authentication, Streamlit, and Gemini**. Gemini is used only for structured invoice autofill; warranty tracking, reminders, and analytics use deterministic backend logic.

## Features

* **Product Management** — Add, update, search, filter, and track products and warranty information.
* **JWT Authentication** — Secure signup/login with user-scoped product and document access.
* **Document Storage** — Upload PDF/JPG/PNG invoices and warranty documents.
* **Shared Invoices** — Many-to-many product-document relationship allows one invoice to belong to multiple products.
* **Invoice Autofill** — Extracts text from text-based PDFs and uses Gemini to generate an editable product preview before saving.
* **Warranty Reminders** — Configurable 30-day, 7-day, and 1-day email reminders with duplicate prevention and delivery tracking.
* **Dashboard** — SQL-based statistics for active, expiring, and expired warranties.

## Architecture

```text
Streamlit
    ↓
FastAPI REST API
    ↓
Pydantic Validation
    ↓
Service Layer
    ↓
SQLAlchemy
    ↓
PostgreSQL / SQLite
```

Backend structure:

```text
backend/
├── database/     # Database sessions
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── routers/      # API endpoints
├── services/     # Business logic
├── ai/           # Invoice extraction
└── utils/        # Auth and shared utilities
```

## Reminder Flow

```text
Warranty expiry
      ↓
User reminder preferences
      ↓
Daily scheduler
      ↓
Check whether reminder is due
      ↓
Prevent duplicates
      ↓
Send email through SMTP
      ↓
Record sent/failed status
```

## Invoice Extraction

```text
Upload invoice
      ↓
Extract PDF text
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

AI-generated data is **never automatically written to the database** without user confirmation.

> **Note:** OCR is not currently implemented. Images can be stored, while extraction is limited to text-based PDFs.

## Tech Stack

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy
**Database:** PostgreSQL / SQLite
**Authentication:** JWT
**AI:** Google Gemini
**Frontend:** Streamlit
**Notifications:** SMTP + scheduled reminders

## Run Locally

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Configure database, JWT, Gemini, SMTP, and upload settings through environment variables in `.env`. Secrets should never be committed to Git.

## Key Backend Concepts

REST APIs • Layered Architecture • JWT Authentication • Authorization • Relational Modelling • Many-to-Many Relationships • SQLAlchemy ORM • File Uploads • Pagination & Filtering • Background Scheduling • Duplicate Prevention • SMTP • Structured AI Output
