from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.database import connect_to_db
from src.api.v1 import main_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    session_factory = await connect_to_db()
    app.state.db_session = session_factory
    yield 

app = FastAPI(
    title="URL Shortener API",
    lifespan=lifespan
)

app.include_router(main_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)