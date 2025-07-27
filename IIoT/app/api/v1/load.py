from fastapi import APIRouter, Depends
from services.services import MQTTService, get_service

LoadService = APIRouter(tags=["loads"])

@LoadService.get("/start")
def start_publishing(mqtt_service: MQTTService = Depends(get_service)):
    mqtt_service.start()
    return {"message": "MQTT publishing started"}

@LoadService.get("/stop")
def stop_publishing(mqtt_service: MQTTService = Depends(get_service)):
    mqtt_service.stop()
    return {"message": "MQTT publishing stopped"}
