from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.models import Motor
from datetime import datetime
from src.core.database import get_db

class MotorRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(self, motor: Motor) -> Motor:
        async with self.session_factory() as session:
            try:
                session.add(motor)
                await session.commit()
                await session.refresh(motor)
                return motor
            except Exception as e:
                await session.rollback()
                raise Exception(f"MotorRepository.create error: {e}")

    async def get_by_id(self, motor_id: str) -> Motor | None:
        async with self.session_factory() as session:
            result = await session.execute(select(Motor).where(Motor.id == motor_id))
            return result.scalar_one_or_none()

    async def delete(self, motor_id: str):
        async with self.session_factory() as session:
            motor = await session.get(Motor, motor_id)
            if motor:
                await session.delete(motor)
                await session.commit()

    async def update_status(self, motor_id: str, status: str):
        async with self.session_factory() as session:
            motor = await session.get(Motor, motor_id)
            if motor:
                motor.status = status
                await session.commit()

def get_motor_repo(session=Depends(get_db)):
    return MotorRepository(session)



