from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.services import mqtt_service
from api.v1 import router_v1

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Lifespan] Starting MQTT publisher")
    mqtt_service.start()
    yield
    print("[Lifespan] Stopping MQTT publisher")
    mqtt_service.stop()

app = FastAPI(
    lifespan=lifespan,
    root_path="/api/iiot-service"
)

app.include_router(router_v1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
