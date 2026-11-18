"""Integration tests for the MQTT security log collector."""

import threading

import pytest
import time

import mqtt_security_monitor as monitor


def wait_for(predicate, timeout=3.0):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)

    return predicate()


@pytest.fixture
def collector(monkeypatch):
    threads = []

    def start(log_path, events):
        original_record = monitor.record_security_event

        def capture(line):
            events.append(line)
            return original_record(line)

        monkeypatch.setattr(
            monitor,
            "record_security_event",
            capture,
        )

        stop_event = threading.Event()

        thread = threading.Thread(
            target=monitor.follow_security_log,
            args=(str(log_path), 0.02, stop_event),
        )
        thread.start()
        threads.append((thread, stop_event))
        return thread

    try:
        yield start
    finally:
        for thread, stop_event in threads:
            stop_event.set()
            thread.join(timeout=2)
            assert not thread.is_alive(), "Collector did not stop"


def test_new_log_entries(tmp_path, collector):
    log = tmp_path / "security.log"
    log.write_text("existing log entry\n")

    events = []
    collector(log, events)

    time.sleep(0.15)

    with log.open("a") as file:
        file.write(
            "Client auto-123 disconnected: not authorised.\n"
        )

    assert wait_for(lambda: len(events) == 1)
    assert "not authorised" in events[0]


def test_incomplete_log_line(tmp_path, collector):
    log = tmp_path / "security.log"
    log.write_text("existing log entry\n")

    events = []
    collector(log, events)

    time.sleep(0.15)

    with log.open("a") as file:
        file.write("Client auto-456 disconnected: not authorised.")

    time.sleep(0.15)
    assert len(events) == 0

    with log.open("a") as file:
        file.write("\n")

    assert wait_for(lambda: len(events) == 1)


def test_log_rotation(tmp_path, collector):
    log = tmp_path / "security.log"
    rotated = tmp_path / "security.log.1"

    log.write_text("existing log entry\n")

    events = []
    collector(log, events)

    time.sleep(0.15)

    log.rename(rotated)
    log.write_text(
        "Client auto-789 disconnected: not authorised.\n"
    )

    assert wait_for(lambda: len(events) == 1)
