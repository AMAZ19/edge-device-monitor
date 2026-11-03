# Edge Device Monitor

A lightweight Linux-based edge device monitor that collects system information and publishes device status via MQTT.

The service runs automatically using systemd and stores the latest device status as JSON while maintaining local log files.

## Features

- Collects hostname, IP address and timestamp
- Generates device status in JSON format
- Runs automatically as a systemd service and timer
- Publishes device status to an MQTT broker
- Uses MQTT retained messages for the latest device state
- Stores local device history in log files
- Uses logrotate for automatic log management
- Simulates industrial sensor telemetry using Python
- Validates incoming MQTT sensor measurements
- Includes automated tests using pytest and code coverage reporting
- Persists validated sensor telemetry in SQLite
- Queries stored telemetry with result limits and device filtering
- Calculates minimum, average, and maximum temperature

## Project Structure

```text
.
├── scripts/
│   └── device_status.sh
├── data/
│   └── device_status.json
├── logs/
│   └── device_status.log
├── device_info.txt
├── .gitignore
└── README.md
```

## Usage

Run the device status collector manually:

```bash
./scripts/device_status.sh
```

View the latest generated device status:
```bash
cat data/device_status.json
```

Monitor the log output in real time:
```bash
tail -f logs/device_status.log
```

Subscribe to the MQTT device status topic:
```bash
mosquitto_sub -h localhost -t "iot/device/status"
```

## Python Device Simulator

The project includes a Python-based industrial IoT simulator
that generates temperature, humidity, and motor current telemetry.

The simulator publishes JSON messages to the MQTT topic
`iot/device/telemetry` using QoS 1.

A separate MQTT consumer subscribes to the telemetry topic,
validates incoming sensor measurements, and stores telemetry
in SQLite when all three sensor values pass validation.

The database is created automatically at `data/telemetry.db`.
Stored measurements remain available after the consumer stops.
Local database files are excluded from Git.

### Telemetry Queries and Statistics

The SQLite storage module supports retrieving the latest stored
measurements, limiting results, and filtering by device ID.
Results are ordered by descending record ID.

Temperature statistics include the measurement count and minimum,
average, and maximum temperature, optionally filtered by device.

Query arguments are validated, and SQL parameters are used for
filter values and result limits.

### Automated Testing

The MQTT consumer includes automated tests covering:

- Valid sensor measurements
- Boundary values and out-of-range measurements
- Invalid data types
- Malformed JSON messages
- MQTT message processing
- SQLite persistence and telemetry queries
- Result ordering, limits, and device filtering
- Temperature statistics and empty query results
- Query argument validation

Latest verified results:

- 45 passing tests using isolated temporary databases
- 78% statement coverage of the MQTT consumer
- 100% statement coverage of the SQLite storage module
- 87% combined statement coverage

Manual verification confirmed MQTT-to-SQLite storage,
persistence after shutdown, and clean shutdown with Ctrl+C.

For installation instructions and technical details,
see [Device Simulator](device-simulator/README.md).
