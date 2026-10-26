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

try:
	while True:
		device = {
			"device_id": os.getenv("DEVICE_ID", "edge-device-001"),
			"temperature": round(random.uniform(20, 30), 2),
			"humidity": round(random.uniform(40, 60), 2),
			"timestamp": datetime.now(timezone.utc).isoformat()
		}

		print(json.dumps(device, indent=4))

		time.sleep(interval)

except KeyboardInterrupt:
	print("\nDevice Simulator stopped gracefully.")
