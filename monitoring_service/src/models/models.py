from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Motor(Base):
    __tablename__ = 'motors'

    id = Column(String, primary_key=True, default="test")
    title = Column(String, default="Тестовый двигатель")
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Motor(id='{self.id}', title='{self.title}')>"


class Defect(Base):
    __tablename__ = 'defects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, default="Тестовый дефект")
    status = Column(String, nullable=True)
    type = Column(String, nullable=True)
    level = Column(Integer, nullable=True)
    forecast = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Defect(id={self.id}, title='{self.title}')>"
