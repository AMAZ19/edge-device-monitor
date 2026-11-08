import json
import sqlite3
from types import SimpleNamespace
from unittest.mock import Mock

import psycopg
import pytest
from prometheus_client import generate_latest

import mqtt_consumer as consumer
from metrics import (
    MQTT_CONNECTED,
    MQTT_MESSAGES_RECEIVED,
    MQTT_INVALID_MESSAGES,
    TELEMETRY_SAVED,
    TELEMETRY_STORAGE_ERRORS,
)


def metric_value(metric, labels=None):
    if labels:
        return metric.labels(**labels)._value.get()
    return metric._value.get()


def message(payload):
    return SimpleNamespace(
        topic="iot/device/telemetry",
        payload=json.dumps(payload).encode("utf-8"),
    )


@pytest.fixture
def valid_device():
    return {
        "device_id": "test-device-001",
        "temperature": 25,
        "humidity": 50,
        "motor_current": 1.5,
        "operating_hours": 100,
        "timestamp": "2026-11-08T12:00:00Z",
    }


def test_metrics_endpoint_format():
    output = generate_latest().decode("utf-8")
    assert "iot_mqtt_messages_received_total" in output
    assert "iot_mqtt_invalid_messages_total" in output
    assert "iot_mqtt_connected" in output


def test_mqtt_connection_status():
    client = Mock()

    consumer.on_connect(client, None, None, 0, None)
    assert metric_value(MQTT_CONNECTED) == 1

    consumer.on_connect(client, None, None, 1, None)
    assert metric_value(MQTT_CONNECTED) == 0


def test_valid_message_metrics(monkeypatch, valid_device):
    monkeypatch.setattr(consumer, "save_telemetry", Mock())
    monkeypatch.setattr(consumer, "save_to_postgres", Mock())

    before_received = metric_value(MQTT_MESSAGES_RECEIVED)
    before_sqlite = metric_value(
        TELEMETRY_SAVED, {"database": "sqlite"}
    )
    before_postgres = metric_value(
        TELEMETRY_SAVED, {"database": "postgres"}
    )

    consumer.on_message(None, None, message(valid_device))

    assert metric_value(MQTT_MESSAGES_RECEIVED) == before_received + 1
    assert metric_value(
        TELEMETRY_SAVED, {"database": "sqlite"}
    ) == before_sqlite + 1
    assert metric_value(
        TELEMETRY_SAVED, {"database": "postgres"}
    ) == before_postgres + 1


def test_invalid_message_metrics(monkeypatch, valid_device):
    sqlite_save = Mock()
    postgres_save = Mock()

    monkeypatch.setattr(consumer, "save_telemetry", sqlite_save)
    monkeypatch.setattr(consumer, "save_to_postgres", postgres_save)

    valid_device["temperature"] = 99

    before = metric_value(MQTT_INVALID_MESSAGES)

    consumer.on_message(None, None, message(valid_device))

    assert metric_value(MQTT_INVALID_MESSAGES) == before + 1
    sqlite_save.assert_not_called()
    postgres_save.assert_not_called()


def test_sqlite_error_metrics(monkeypatch, valid_device):
    monkeypatch.setattr(
        consumer,
        "save_telemetry",
        Mock(side_effect=sqlite3.OperationalError("test failure")),
    )
    postgres_save = Mock()
    monkeypatch.setattr(consumer, "save_to_postgres", postgres_save)

    before = metric_value(
        TELEMETRY_STORAGE_ERRORS, {"database": "sqlite"}
    )

    consumer.on_message(None, None, message(valid_device))

    assert metric_value(
        TELEMETRY_STORAGE_ERRORS, {"database": "sqlite"}
    ) == before + 1
    postgres_save.assert_not_called()


def test_postgres_error_metrics(monkeypatch, valid_device):
    monkeypatch.setattr(consumer, "save_telemetry", Mock())
    monkeypatch.setattr(
        consumer,
        "save_to_postgres",
        Mock(side_effect=psycopg.OperationalError("test failure")),
    )

    before = metric_value(
        TELEMETRY_STORAGE_ERRORS, {"database": "postgres"}
    )

    consumer.on_message(None, None, message(valid_device))

    assert metric_value(
        TELEMETRY_STORAGE_ERRORS, {"database": "postgres"}
    ) == before + 1


def test_mqtt_disconnect_status():
    consumer.on_connect(Mock(), None, None, 0, None)
    assert metric_value(MQTT_CONNECTED) == 1

    consumer.on_disconnect(Mock(), None, None, 0, None)
    assert metric_value(MQTT_CONNECTED) == 0
