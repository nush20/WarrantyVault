import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.session import Base, engine
from backend.routers import analytics, auth, documents, notifications, products
from backend.services.reminder_service import reminder_worker, stop_reminder_worker
from backend.utils.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    reminder_task = asyncio.create_task(reminder_worker())
    try:
        yield
    finally:
        await stop_reminder_worker(reminder_task)


app = FastAPI(
    title="WarrantyVault API",
    version="1.0.0",
    description="Manage products, warranty dates, claim details, documents, and reminders.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(documents.router)
app.include_router(analytics.router)
app.include_router(notifications.router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
