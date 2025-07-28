from fastapi import Depends
from src.repositories.defect import DefectRepository, get_defect_repo
from src.models import Defect
from src.core.logging import Logger


class DefectService:
    def __init__(self, repository: DefectRepository):
        self.repo = repository

    async def create_defect(self, defect: Defect) -> Defect:
        try:
            defectDB = await self.repo.get_by_id(defect.id)
            if defectDB: return defectDB
            return await self.repo.create(defect)
        except Exception as e:
            Logger.error(f"DefectService: create_defect: {e}")

    async def get_defect(self, defect_id: int) -> Defect | None:
        try:
            return await self.repo.get_by_id(defect_id)
        except Exception as e:
            Logger.error(f"DefectService: get_defect: {e}")

    async def update_status(self, defect_id: int, status: str):
        try:
            await self.repo.update_status(defect_id, status)
            return await self.repo.get_by_id(defect_id)
        except Exception as e:
            Logger.error(f"DefectService: update_status: {e}")

    async def update_level(self, defect_id: int, level: int):
        try:
            await self.repo.update_level(defect_id, level)
            return await self.repo.get_by_id(defect_id)
        except Exception as e:
            Logger.error(f"DefectService: update_level: {e}")

    async def update_forecast(self, defect_id: int, forecast: int):
        try:
            await self.repo.update_forecast(defect_id, forecast)
            return await self.repo.get_by_id(defect_id)
        except Exception as e:
            Logger.error(f"DefectService: update_forecast: {e}")

    async def delete_defect(self, defect_id: int):
        try:
            await self.repo.delete(defect_id)
        except Exception as e:
            Logger.error(f"DefectService: delete_defect: {e}")


def get_defect_service(repo: DefectRepository = Depends(get_defect_repo)):
    return DefectService(repo)
