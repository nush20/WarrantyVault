# WarrantyVault

WarrantyVault is an interview-friendly warranty manager built with FastAPI, SQLAlchemy, PostgreSQL-compatible
models, JWT authentication, Streamlit, and a small optional Gemini invoice-prefill feature. It keeps products,
expiry dates, claim information, and supporting documents together.

The project deliberately does not include RAG, vector databases, OCR, Docker, queues, or microservices.

## Architecture

```text
Streamlit -> FastAPI routers -> services -> SQLAlchemy -> SQLite locally / PostgreSQL in deployment
                                      |-> local document storage
                                      |-> Gemini invoice extraction (optional)
                                      |-> daily reminder worker
```

- `backend/routers`: authenticated HTTP endpoints and validation boundaries.
- `backend/services`: product rules, ownership checks, file handling, and reminders.
- `backend/models` and `backend/database`: relational persistence.
- `backend/ai/extractor.py`: text-based PDF extraction and optional invoice field extraction.
- `streamlit_app.py`: a small demonstration interface, not a separate frontend architecture.

## Local setup

```bash
cd "/Users/anushkanandwani/Documents/Codex/2026-09-02/build-a-backend-focused-project-called"
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
# Add GEMINI_API_KEY only if you want invoice prefill.
python -m uvicorn backend.main:app --reload
```

Open Swagger at <http://localhost:8000/docs>. SQLite is the zero-setup local default. Set `DATABASE_URL` to a
PostgreSQL URL for deployment. Tables are created at startup for demo simplicity; production would use Alembic.

Start the interface in a second terminal:

```bash
source .venv/bin/activate
python -m streamlit run streamlit_app.py
```

Open <http://localhost:8501>.

## Product workflow

Users can add a product manually or upload a text-based invoice PDF. Extraction returns invoice-level details
and every detected product line. The editable review lets users exclude fees, discounts, accessories, or bad
detections before saving. Only confirmation creates product records. A shared invoice is then linked to every
selected product through `product_documents`, so documents and products have a many-to-many relationship.

Each product can store:

- Purchase details: product, category, brand, seller, purchase date, and price.
- Warranty details: expiry date, serial number, invoice number, and provider.
- Claim details: support URL, phone, email, and notes.
- Attached invoice, warranty-card, and supporting PDF/image files.
- Per-product 30-day, 7-day, and 1-day reminder preferences.

The dashboard shows only warranty-relevant information: total products, active warranties, expiring warranties,
expired warranties, upcoming expirations, and recently added products.

## Important endpoints

- `POST /auth/signup` and `POST /auth/login`: account creation and JWT login.
- `POST/GET /products`: create, filter, paginate, and list products.
- `GET/PATCH/DELETE /products/{id}`: product details and CRUD.
- `GET /products/expiring?days=30`: warranties ending within a window.
- `GET/PUT /products/{id}/reminders`: product-specific reminder preferences.
- `POST /documents`: attach a PDF/image to a product, or upload an invoice before extraction.
- `GET /documents?product_id={id}`: documents belonging to one product.
- `GET /documents/{id}/download`: authenticated document download.
- `DELETE /documents/{id}`: remove an unwanted or duplicate product document.
- `POST /documents/{id}/extract`: return an editable invoice-field preview.
- `POST /documents/{id}/confirm`: validate and save the selected reviewed products, then link the invoice to all.
- `GET /analytics/summary`: warranty-status counts used by the dashboard.
- `POST /notifications/generate`: run the reminder check immediately for a demo.

## Reminder behavior

The in-process worker runs daily at 9 AM in `REMINDER_TIMEZONE`. For every product it derives the selected
reminder dates from `warranty_expiry_date`, creates only reminders that are due, and uses a database uniqueness
constraint to prevent duplicates. Each email attempt is recorded as `pending`, `sent`, or `failed`, with its
attempt count and send time; failures are retried up to three times by later runs. Configure `SMTP_HOST`,
`SMTP_PORT`, `SMTP_FROM_EMAIL`, and optional SMTP credentials in `.env`. The same reminder and delivery state
remain visible in the dashboard. A production deployment with multiple API instances should invoke the service
from one platform-scheduled job.

## Document limitations

Files are stored locally and metadata is stored in SQL. Text extraction supports text-based PDFs through
`pypdf`. JPEG/PNG files and scanned PDFs can still be kept as proof, but OCR is intentionally not included.

## Tests

```bash
source .venv/bin/activate
pytest
```

The endpoint tests cover authentication, ownership-protected product CRUD, expiry calculation, filtering,
dashboard counts, document metadata/list/download, invoice review-before-save, and idempotent reminders.

## Interview talking points

- Every product and document query is scoped to the authenticated user.
- Warranty status and dashboard counts are relational queries, not AI features.
- Reminder dates are derived from each product's expiry, emailed independently of app usage, and protected
  against duplicate delivery.
- Invoice extraction is convenience-only: Pydantic validates an item array and the user selects what to persist.
- A junction table lets one invoice support several products and one product keep several claim documents.
