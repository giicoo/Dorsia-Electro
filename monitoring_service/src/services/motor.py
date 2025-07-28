from fastapi import Depends
from src.repositories.motor import MotorRepository, get_motor_repo
from src.models import Motor
from src.core.logging import Logger


class MotorService:
    def __init__(self, repository: MotorRepository):
        self.repo = repository

    async def create_motor(self, motor: Motor) -> Motor:
        try:
            motorDB = await self.repo.get_by_id(motor.id)
            if motorDB: return motorDB
            return await self.repo.create(motor)
        except Exception as e:
            Logger.error(f"MotorService: create_motor: {e}")

    async def get_motor(self, motor_id: str) -> Motor | None:
        try:
            return await self.repo.get_by_id(motor_id)
        except Exception as e:
            Logger.error(f"MotorService: get_motor: {e}")

    async def update_status(self, motor_id: str, status: str):
        try:
            await self.repo.update_status(motor_id, status)
            return await self.repo.get_by_id(motor_id)
        except Exception as e:
            Logger.error(f"MotorService: update_status: {e}")

    async def delete_motor(self, motor_id: str):
        try:
            await self.repo.delete(motor_id)
        except Exception as e:
            Logger.error(f"MotorService: delete_motor: {e}")


def get_motor_service(repo: MotorRepository = Depends(get_motor_repo)):
    return MotorService(repo)
