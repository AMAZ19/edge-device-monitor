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

## Usage

Run the device status collector manually:

```bash
./scripts/device_status.sh
cat data/device_status.json
tail -f logs/device_status.log
mosquitto_sub -h localhost -t "iot/device/status"
