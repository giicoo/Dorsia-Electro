from fastapi import APIRouter
from src.api.v1.motor import router as motor
from src.api.v1.defect import router as defect

main_router = APIRouter()
main_router.include_router(motor)
main_router.include_router(defect)