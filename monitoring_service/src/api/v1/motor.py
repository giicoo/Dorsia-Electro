# src/routers/motor_router.py
from fastapi import APIRouter, Depends, HTTPException
from src.models.models import Motor
from src.services.motor import MotorService, get_motor_service
from src.schemas.motor import MotorCreate, MotorUpdateStatus, MotorOut

router = APIRouter(prefix="/motors", tags=["Motors"])


@router.post("/", response_model=MotorOut)
async def create_motor(payload: MotorCreate, service: MotorService = Depends(get_motor_service)):
    motor = Motor(**payload.model_dump())
    motor = await service.create_motor(motor)
    return motor


@router.get("/{motor_id}", response_model=MotorOut)
async def get_motor(motor_id: str, service: MotorService = Depends(get_motor_service)):
    motor = await service.get_motor(motor_id)
    if not motor:
        raise HTTPException(status_code=404, detail="Motor not found")
    return motor


@router.patch("/{motor_id}/status", response_model=MotorOut)
async def update_status(motor_id: str, payload: MotorUpdateStatus, service: MotorService = Depends(get_motor_service)):
    result = await service.update_status(motor_id, payload.status)
    if not result:
        raise HTTPException(status_code=404, detail="Motor not found")
    return result


@router.delete("/{motor_id}")
async def delete_motor(motor_id: str, service: MotorService = Depends(get_motor_service)):
    await service.delete_motor(motor_id)
    return {"status": "deleted"}
