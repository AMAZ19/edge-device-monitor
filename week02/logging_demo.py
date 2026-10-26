import logging

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s | %(levelname)s | %(message)s",
	filename="device.log",
	filemode="a"
)

logging.info("IoT Device Simulator started")
logging.warning("Temperature approaching limit")
logging.error("Sensor communication failed")

