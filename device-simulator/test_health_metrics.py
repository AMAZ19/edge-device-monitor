import sqlite3
from unittest.mock import Mock

import psycopg

import mqtt_consumer as consumer
from metrics import (
    LAST_MESSAGE_TIMESTAMP,
    LAST_SAVED_TIMESTAMP,
)
from test_metrics import message, metric_value


DEVICE = {
    "device_id": "health-test-001",
    "temperature": 25,
    "humidity": 50,
    "motor_current": 1.5,
    "operating_hours": 100,
    "timestamp": "2026-11-09T12:00:00Z",
}


def test_message_timestamp(monkeypatch):
    monkeypatch.setattr(consumer, "save_telemetry", Mock())
    monkeypatch.setattr(consumer, "save_to_postgres", Mock())
    monkeypatch.setattr(consumer.time, "time", lambda: 1234567890)

    consumer.on_message(None, None, message(DEVICE))

    assert metric_value(LAST_MESSAGE_TIMESTAMP) == 1234567890


def test_successful_storage_timestamps(monkeypatch):
    monkeypatch.setattr(consumer, "save_telemetry", Mock())
    monkeypatch.setattr(consumer, "save_to_postgres", Mock())
    monkeypatch.setattr(consumer.time, "time", lambda: 1234567891)

    consumer.on_message(None, None, message(DEVICE))

    assert metric_value(
        LAST_SAVED_TIMESTAMP, {"database": "sqlite"}
    ) == 1234567891

    assert metric_value(
        LAST_SAVED_TIMESTAMP, {"database": "postgres"}
    ) == 1234567891


def test_sqlite_failure_does_not_update_storage(monkeypatch):
    monkeypatch.setattr(
        consumer, "save_telemetry",
        Mock(side_effect=sqlite3.OperationalError("failed"))
    )
    monkeypatch.setattr(consumer, "save_to_postgres", Mock())
    monkeypatch.setattr(consumer.time, "time", lambda: 1234567892)

    before = metric_value(
        LAST_SAVED_TIMESTAMP, {"database": "sqlite"}
    )

    consumer.on_message(None, None, message(DEVICE))

    assert metric_value(
        LAST_SAVED_TIMESTAMP, {"database": "sqlite"}
    ) == before


def test_postgres_failure_does_not_update_timestamp(monkeypatch):
    monkeypatch.setattr(consumer, "save_telemetry", Mock())
    monkeypatch.setattr(
        consumer, "save_to_postgres",
        Mock(side_effect=psycopg.OperationalError("failed"))
    )
    monkeypatch.setattr(consumer.time, "time", lambda: 1234567893)

    before = metric_value(
        LAST_SAVED_TIMESTAMP, {"database": "postgres"}
    )

    consumer.on_message(None, None, message(DEVICE))

    assert metric_value(
        LAST_SAVED_TIMESTAMP, {"database": "postgres"}
    ) == before
