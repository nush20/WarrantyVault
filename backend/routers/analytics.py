from fastapi import APIRouter, Query

from backend.schemas.analytics import AnalyticsSummary
from backend.services.analytics_service import summary
from backend.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    db: DbSession,
    user: CurrentUser,
    expiring_within_days: int = Query(30, ge=0, le=3650),
):
    return summary(db, user.id, expiring_within_days)
