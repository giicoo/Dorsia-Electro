# src/routers/defect_router.py
from fastapi import APIRouter, Depends, HTTPException
from src.models.models import Defect
from src.services.defect import DefectService, get_defect_service
from src.schemas.defect import (
    DefectCreate, DefectUpdateStatus,
    DefectUpdateForecast, DefectUpdateLevel,
    DefectOut
)

router = APIRouter(prefix="/defects", tags=["Defects"])


@router.post("/", response_model=DefectOut)
async def create_defect(payload: DefectCreate, service: DefectService = Depends(get_defect_service)):
    defect = Defect(**payload.model_dump())
    defect = await service.create_defect(defect)
    return defect


@router.get("/{defect_id}", response_model=DefectOut)
async def get_defect(defect_id: int, service: DefectService = Depends(get_defect_service)):
    defect = await service.get_defect(defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    return defect


@router.patch("/{defect_id}/status", response_model=DefectOut)
async def update_status(defect_id: int, payload: DefectUpdateStatus, service: DefectService = Depends(get_defect_service)):
    result = await service.update_status(defect_id, payload.status)
    if not result:
        raise HTTPException(status_code=404, detail="Defect not found")
    return result


@router.patch("/{defect_id}/forecast", response_model=DefectOut)
async def update_forecast(defect_id: int, payload: DefectUpdateForecast, service: DefectService = Depends(get_defect_service)):
    result = await service.update_forecast(defect_id, payload.forecast)
    if not result:
        raise HTTPException(status_code=404, detail="Defect not found")
    return result


@router.patch("/{defect_id}/level", response_model=DefectOut)
async def update_level(defect_id: int, payload: DefectUpdateLevel, service: DefectService = Depends(get_defect_service)):
    result = await service.update_level(defect_id, payload.level)
    if not result:
        raise HTTPException(status_code=404, detail="Defect not found")
    return result


@router.delete("/{defect_id}")
async def delete_defect(defect_id: int, service: DefectService = Depends(get_defect_service)):
    await service.delete_defect(defect_id)
    return {"status": "deleted"}
