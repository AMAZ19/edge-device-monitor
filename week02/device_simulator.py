import json
import random
import time
from datetime import datetime, timezone

try:
	while True:
		device = {
			"device_id": "edge-device-001",
			"temperature": round(random.uniform(20, 30), 2),
			"humidity": round(random.uniform(40, 60), 2),
			"timestamp": datetime.now(timezone.utc).isoformat()
		}

		print(json.dumps(device, indent=4))

		time.sleep(5)

except KeyboardInterrupt:
	print("\nDevice Simulator stopped gracefully.")
