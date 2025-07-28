from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.core.database import get_db
from src.models import Defect

class DefectRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, defect: Defect) -> Defect:
        async with self.session_factory() as session:
            try:
                session.add(defect)
                await session.commit()
                await session.refresh(defect)
                return defect
            except Exception as e:
                await session.rollback()
                raise Exception(f"DefectRepository.create error: {e}")

    async def get_by_id(self, defect_id: int) -> Defect | None:
        async with self.session_factory() as session:
            result = await session.execute(select(Defect).where(Defect.id == defect_id))
            return result.scalar_one_or_none()

    async def delete(self, defect_id: int):
        async with self.session_factory() as session:
            defect = await session.get(Defect, defect_id)
            if defect:
                await session.delete(defect)
                await session.commit()

    async def update_status(self, defect_id: int, status: str):
        async with self.session_factory() as session:
            defect = await session.get(Defect, defect_id)
            if defect:
                defect.status = status
                await session.commit()
    
    async def update_level(self, defect_id: int, level: int):
        async with self.session_factory() as session:
            defect = await session.get(Defect, defect_id)
            if defect:
                defect.level = level
                await session.commit()

    async def update_forecast(self, defect_id: int, forecast: int):
        async with self.session_factory() as session:
            defect = await session.get(Defect, defect_id)
            if defect:
                defect.forecast = forecast
                await session.commit()


def get_defect_repo(session=Depends(get_db)):
    return DefectRepository(session)