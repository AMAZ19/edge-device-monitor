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

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
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
	print("\nDevice Simulator stopped gracefully.")
