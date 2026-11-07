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
- Provides a command-line interface for telemetry queries and statistics

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

### Telemetry Command-Line Interface

From the `device-simulator` directory, retrieve stored measurements
or calculate temperature statistics:

```bash
.venc/bin/python telemetry_cli.py latest --limit 3
.venc/bin/python telemetry_cli.py stats --device-id week04-mqtt-test
```

The database must already have been initialized by the consumer.
Both commands support optional device filtering and print formatted
JSON. Invalid arguments return exit code 2; database errors return
exit code 1.

Use `telemetry_cli.py --help` for available commands and options.

### Automated Testing

The Python components include automated tests covering:

- Valid sensor measurements
- Boundary values and out-of-range measurements
- Invalid data types
- Malformed JSON messages
- MQTT message processing
- SQLite persistence and telemetry queries
- Result ordering, limits, and device filtering
- Temperature statistics and empty query results
- Query argument validation
- CLI JSON output and command options
- CLI argument validation and database error handling

Latest verified results:

- 54 passing tests; storage tests use isolated temporary databases
- 78% statement coverage of the MQTT consumer
- 100% statement coverage of the SQLite storage module
- 96% statement coverage of the telemetry CLI
- 89% combined statement coverage

Manual verification confirmed MQTT-to-SQLite storage,
persistence after shutdown, and clean shutdown with Ctrl+C.

For installation instructions and technical details,
see [Device Simulator](device-simulator/README.md).

## Monitoring and MQTT Alerting

### Architecture

Device Simulator -> Mosquitto -> MQTT Consumer -> PostgreSQL -> Grafana -> MQTT Alerts

Validated telemetry is stored in SQLite and PostgreSQL.

### Grafana Dashboard

Dashboard: `IoT Device Monitor`

The dashboard visualizes:
- Temperature (°C)
- Humidity (%)
- Motor current (A)

Data source: PostgreSQL (`iot_telemetry`).

### Temperature Alert

- Rule: `IoT Device - High Temperature Alert`
- Device: `edge-device-001`
- Threshold: Temperature > 28 °C
- Pending period: 0 seconds
- Contact point: `IoT MQTT Alerts`
- MQTT topic: `iot/device/alerts`
- Message format: JSON

### End-to-End Test

Successfully verified on November 7, 2026.

Grafana detected 28.83 °C and published a firing
notification through MQTT.

### Monitor MQTT Alerts

Run:

    mosquitto_sub -h localhost -t 'iot/device/alerts' -v

### Security

Database credentials are stored in local environment files.
The MQTT broker currently listens on localhost.
Production deployments should use MQTT authentication and TLS.
