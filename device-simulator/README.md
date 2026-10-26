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
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
