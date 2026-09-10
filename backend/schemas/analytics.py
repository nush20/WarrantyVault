from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_products: int
    active_warranties: int
    expired_warranties: int
    expiring_soon: int
    expiring_within_days: int
