import paho.mqtt.client as mqtt
import json
from telemetry_storage import initialize_database, save_telemetry
import sqlite3
import psycopg
from postgres_storage import save_telemetry as save_to_postgres

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

        try:
                print(f"Payload: {msg.payload.decode('utf-8')}")
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

                sensor_checks = (
                    validate_sensor_value(temperature, 20, 30)[0],
                    validate_sensor_value(humidity, 40, 60)[0],
                    validate_sensor_value(motor_current, 0.5, 2.5)[0],
                )

                if all(sensor_checks):
                    save_telemetry(device)
                    print("Telemetry saved to SQLite.")

                    try:
                        save_to_postgres(device)
                        print("Telemetry saved to PostgreSQL.")
                    except psycopg.Error as error:
                        print(f"PostgreSQL error: {error}")
                else:
                    print("Telemetry not saved: sensor validation failed.")

        except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as error:
                print(f"Invalid sensor data: {error}")
        except sqlite3.Error as error:
                print(f"Database error: {error}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

if __name__ == "__main__":
    initialize_database()

    try:
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\nConsumer stopped.")
    finally:
        mqtt_client.disconnect()
