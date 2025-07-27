from fastapi import APIRouter
from api.v1.load import LoadService
from api.v1.metrics import MetricsService

router_v1 = APIRouter()

router_v1.include_router(LoadService)
router_v1.include_router(MetricsService)
