import random
import threading
import time
import paho.mqtt.client as mqtt
import json

class MQTTService:
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883
    MQTT_TOPIC_PREFIX = "motor"

    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        self.running = False
        self.thread = None

    def publish_loop(self):
        while self.running:
            id = "MQ12R"
            current_T = round(random.uniform(0, 100), 2)
            current_R = round(random.uniform(0, 100), 2)
            current_S = round(random.uniform(0, 100), 2)

            payload = json.dumps({"id": id, "current_T": current_T, "current_R": current_R, "current_S": current_S})

            self.client.publish(f"{self.MQTT_TOPIC_PREFIX}/electro", payload)
            print(f"[MQTT] id={id} T={current_T}, R={current_R}, S={current_S}")
            time.sleep(1)

    def start(self):
        if self.running:
            print("[MQTT] Publisher already running")
            return
        self.running = True
        self.thread = threading.Thread(target=self.publish_loop, daemon=True)
        self.thread.start()
        print("[MQTT] Publisher started")

    def stop(self):
        if not self.running:
            print("[MQTT] Publisher not running")
            return
        self.running = False
        self.thread.join()
        print("[MQTT] Publisher stopped")

mqtt_service = MQTTService()

def get_service():
    return mqtt_service
