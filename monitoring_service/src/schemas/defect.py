# src/schemas/defect.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DefectCreate(BaseModel):
    id: int
    title: str
    status: Optional[str] = None
    type: Optional[str] = None
    level: Optional[int] = None
    forecast: Optional[int] = None

    class Config:
        from_attributes = True


class DefectUpdateStatus(BaseModel):
    status: str


class DefectUpdateLevel(BaseModel):
    level: int


class DefectUpdateForecast(BaseModel):
    forecast: int


class DefectOut(BaseModel):
    id: int
    title: str
    status: Optional[str]
    type: Optional[str]
    level: Optional[int]
    forecast: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
