from prometheus_client import Counter, Gauge, start_http_server

MQTT_MESSAGES_RECEIVED = Counter(
    "iot_mqtt_messages_received_total",
    "Total number of received MQTT messages",
)

MQTT_INVALID_MESSAGES = Counter(
    "iot_mqtt_invalid_messages_total",
    "Total number of invalid MQTT messages",
)

MQTT_CONNECTED = Gauge(
    "iot_mqtt_connected",
    "MQTT connection status: 1 connected, 0 disconnected",
)

TELEMETRY_SAVED = Counter(
    "iot_telemetry_saved_total",
    "Successful telemetry storage operations",
    ["database"],
)

TELEMETRY_STORAGE_ERRORS = Counter(
    "iot_telemetry_storage_errors_total",
    "Telemetry storage errors",
    ["database"],
)



LAST_MESSAGE_TIMESTAMP = Gauge(
    "iot_last_message_timestamp_seconds",
    "Unix timestamp of the last received MQTT message",
)

LAST_SAVED_TIMESTAMP = Gauge(
    "iot_last_saved_timestamp_seconds",
    "Unix timestamp of the last successful telemetry storage",
    ["database"],
)


def start_metrics_server(port=8000):
    start_http_server(port)


TEMPERATURE = Gauge(
    "iot_temperature_celsius",
    "Latest valid temperature in Celsius",
)

HUMIDITY = Gauge(
    "iot_humidity_percent",
    "Latest valid relative humidity percentage",
)

MOTOR_CURRENT = Gauge(
    "iot_motor_current_amperes",
    "Latest valid motor current in amperes",
)
