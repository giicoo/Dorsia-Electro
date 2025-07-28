# src/schemas/motor.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MotorCreate(BaseModel):
    id: str
    title: str
    status: Optional[str] = None

    class Config:
        from_attributes = True


class MotorUpdateStatus(BaseModel):
    status: str


class MotorOut(BaseModel):
    id: str
    title: str
    status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
