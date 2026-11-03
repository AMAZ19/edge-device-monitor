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
This project uses simulated measurements for local development and testing. The operating hours counter resets when the simulator restarts. MQTT authentication and TLS encryption are not yet implemented.

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

## Persistent Telemetry Storage

The MQTT consumer stores telemetry in SQLite when all three sensor
measurements pass validation. Messages with out-of-range sensor values
are not stored.

The database is created automatically at `../data/telemetry.db`,
relative to this directory. Its location is independent of the
working directory used to start the consumer.

Each record contains:

- An automatically assigned ID
- Device ID
- Timestamp
- Temperature
- Humidity
- Motor current
- Operating hours

The storage module uses parameterized SQL statements, commits
successful transactions, and explicitly closes database connections.

Database errors are reported by the consumer. Press Ctrl+C to
disconnect and stop the consumer.

The local database and its companion files are excluded from Git.

## Telemetry Queries and Statistics

Run these examples from the `device-simulator` directory after
the consumer has initialized the database.

Retrieve the latest three stored measurements:

```bash
.venc/bin/python -c "from telemetry_storage import get_latest_telemetry; from pprint import pprint; pprint(get_latest_telemetry(limit=3))"
```

Retrieve measurements for one device:

```bash
.venc/bin/python -c "from telemetry_storage import get_latest_telemetry; from pprint import pprint; pprint(get_latest_telemetry(device_id='week04-mqtt-test'))"
```

`get_latest_telemetry` returns a list of dictionaries, ordered by
descending record ID (most recently stored first). The default
limit is 10. An empty result returns an empty list.

The limit must be a positive integer; booleans are rejected.
An optional device ID must be a non-empty string.
Invalid arguments raise `ValueError`.

Calculate temperature statistics across all stored measurements:

```bash
.venc/bin/python -c "from telemetry_storage import get_temperature_statistics; from pprint import pprint; pprint(get_temperature_statistics())"
```

Pass `device_id` to restrict statistics to one device.

The result contains the measurement count and minimum, average,
and maximum temperature. When no measurements match, the count
is zero and the temperature statistics are `None`.

Queries use SQL parameters for filter values and limits.
Database connections are explicitly closed after each query.

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
.venc/bin/python -m pytest test_mqtt_consumer.py --cov=mqtt_consumer --cov=telemetry_storage --cov-report=term-missing
```

### Test Results

- 45 automated tests passing
- 78% statement coverage of `mqtt_consumer.py`
- 100% statement coverage of `telemetry_storage.py`
- 87% combined statement coverage

Tests cover sensor validation, malformed JSON, MQTT message
processing, successful database insertion, and rejection of
out-of-range measurements.

Query tests cover ordering, result limits, device filtering,
temperature statistics, empty results, and invalid arguments.
Each test uses an isolated temporary database.

Uncovered code includes MQTT connection handling, database error
handling, and application startup and shutdown.

Manual verification confirmed MQTT-to-SQLite storage, persistence
after consumer shutdown, and clean shutdown with Ctrl+C.
