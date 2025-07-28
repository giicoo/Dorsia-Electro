import json
from prometheus_client import start_http_server, Gauge
import paho.mqtt.client as mqtt

# Словарь метрик с лейблом id
metrics = {}

def get_metric_for_id(metric_name, device_id):
    # Создаёт метрику с лейблом 'id', если ещё не создана
    key = (metric_name, device_id)
    if key not in metrics:
        metrics[key] = Gauge(metric_name, 'Metric from MQTT', ['id'])
    return metrics[key]

def on_message(client, userdata, msg):
    try:
        print(f"Received MQTT message on topic {msg.topic}: {msg.payload}")
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("id")
        if not device_id:
            print("No id in payload, skipping")
            return
        for metric_name, value in payload.items():
            if metric_name == "id":
                continue
            metric = get_metric_for_id(metric_name, device_id)
            metric.labels(id=device_id).set(float(value))
            print(f"Set metric {metric_name} with id={device_id} to {value}")
    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    start_http_server(9100)  # Порт для Prometheus scrape
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
    client.on_message = on_message
    client.connect("mosquitto", 1883, 60)
    client.subscribe("motor/#")
    client.loop_forever()

if __name__ == "__main__":
    main()
