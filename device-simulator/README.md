# Industrial IoT Device Simulator

A Python-based industrial IoT device simulator that generates synthetic sensor telemetry and publishes it to a local MQTT broker.

## Features

- Simulated temperature, humidity, and motor current measurements
- Operating hours tracking
- Configurable device ID and measurement interval
- Input validation for measurement intervals
- JSON-formatted telemetry with UTC timestamps
- MQTT publishing using Paho MQTT (QoS 1)
- Graceful shutdown using Ctrl+C

## Technology Stack

- Python 3
- Eclipse Mosquitto MQTT Broker
- Paho MQTT Client
- Git

## Installation

Create and activate a Python virtual environment:

```bash
python3 -m venv .venc
.venc/bin/python -m pip install -r requirements.txt
```

Ensure that a local Mosquitto MQTT broker is running on port 1883.

## Usage

```bash
python device_simulator.py
```

Optional environment variables:

```bash
DEVICE_ID=industrial-device-001 MEASUREMENT_INTERVAL=5 python device_simulator.py
```

## MQTT Configuration

- Broker: localhost
- Port: 1883
- Topic: iot/device/telemetry
- Quality of Service: 1

## Example Telemetry

```json
{
  "device_id": "edge-device-001",
  "temperature": 25.45,
  "humidity": 55.51,
  "motor_current": 2.11,
  "operating_hours": 0.0014,
  "timestamp": "2026-10-26T19:00:11+00:00"
}
```

## Notes

This project uses simulated measurements for local development and testing. The operating hours counter resets when the application restarts. MQTT authentication, TLS encryption, and persistent telemetry storage are not yet implemented.

## MQTT Telemetry Consumer

The MQTT consumer subscribes to `iot/device/telemetry`, decodes JSON messages, and validates incoming sensor measurements.

### Sensor Validation

| Sensor | Valid Range | Unit |
|---|---|---|
| Temperature | 20–30 | °C |
| Humidity | 40–60 | % |
| Motor Current | 0.5–2.5 | A |

Invalid data types and out-of-range measurements are reported without stopping the consumer. Malformed JSON messages are handled gracefully.

### Run the Consumer

```bash
.venc/bin/python mqtt_consumer.py
```

## Automated Testing

The project uses pytest for automated sensor validation and MQTT message-processing tests.

Install development dependencies:

```bash
.venc/bin/python -m pip install -r requirements-dev.txt
```

Run the test suite:

```bash
.venc/bin/python -m pytest test_mqtt_consumer.py -v
```

Measure code coverage:

```bash
.venc/bin/python -m pytest test_mqtt_consumer.py --cov=mqtt_consumer --cov-report=term-missing
```

### Test Results

- 17 automated tests passing
- 87% statement coverage of `mqtt_consumer.py` at the latest verified test run
- Coverage includes sensor validation, boundary values, invalid data types, and simulated MQTT messages

The remaining uncovered code includes MQTT connection handling and application startup, which require additional integration testing.
