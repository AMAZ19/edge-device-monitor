import paho.mqtt.client as mqtt
import os
import json
import random
import time
from datetime import datetime, timezone

try:
	interval = float((os.getenv("MEASUREMENT_INTERVAL", "5")))
	if interval <= 0:
		raise ValueError("Measurement interval must be positiv")
except ValueError:
	print("Invalid measurement interval. Using default: 5 seconds.")
	interval = 5.0

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT connection established successfully.")
    else:
        print(f"MQTT connection failed: {reason_code}")

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"MQTT message {mid} acknowledged by broker.")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"MQTT disconnected: {reason_code}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_disconnect = on_disconnect
mqtt_client.reconnect_delay_set(min_delay=1, max_delay=30)
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()
start_time = time.monotonic()

try:
	while True:

		device = {
			"device_id": os.getenv("DEVICE_ID", "edge-device-001"),
			"temperature": round(random.uniform(20, 30), 2),
			"humidity": round(random.uniform(40, 60), 2),
			"motor_current": round(random.uniform(0.5, 2.5), 2),
			"operating_hours": round((time.monotonic() - start_time) / 3600, 4),
			"timestamp": datetime.now(timezone.utc).isoformat()
		}

		print(json.dumps(device, indent=4))
		mqtt_client.publish("iot/device/telemetry", json.dumps(device), qos=1)

		time.sleep(interval)

except KeyboardInterrupt:
    print("\nStopping Device Simulator...")

finally:
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    print("Device Simulator stopped gracefully.")
