import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, reason_code, properties):
	if reason_code == 0:
		print("consumer connected to MQTT broker.")
		client.subscribe("iot/device/telemetry", qos=1)
	else:
		print(f"connection failed: {reason_code}")

def validate_sensor_value(value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False, "Invalid data type"

    if not minimum <= value <= maximum:
        return False, "Out of range"

    return True, "Valid"

def on_message(client, userdata, msg):
	print(f"Message received on topic: {msg.topic}")
	print(f"Payload: {msg.payload.decode('utf-8')}")

	try:
		device = json.loads(msg.payload.decode("utf-8"))

		print(f"Device ID: {device['device_id']}")
		print(f"Temperature: {device['temperature']} °C")
		temperature = device["temperature"]
		is_valid, reason = validate_sensor_value(temperature, 20, 30)

		if is_valid:
		    print("Temperature validation: PASSED")
		else:
		    print(f"Temperature validation: FAILED - {reason}")
		
		print(f"Humidity: {device['humidity']} %")
		humidity = device["humidity"]
		is_valid, reason = validate_sensor_value(humidity, 40, 60)

		if is_valid:
		    print("Humidity validation: PASSED")
		else:
		    print(f"Humidity validation: FAILED - {reason}")
		
		print(f"Motor Current: {device['motor_current']} A")
		motor_current = device["motor_current"]
		is_valid, reason = validate_sensor_value(motor_current, 0.5, 2.5)

		if is_valid:
		    print("Motor Current validation: PASSED")
		else:
		    print(f"Motor Current validation: FAILED - {reason}")

	except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as error:
		print(f"Invalid sensor data: {error}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

if __name__ == "__main__":
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_forever()
