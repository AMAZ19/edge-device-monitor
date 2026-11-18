"""Parse Mosquitto security events from broker logs."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SecurityEvent:
    event_type: str
    message: str
    client_id: Optional[str] = None


def parse_security_event(line: str) -> Optional[SecurityEvent]:
    """Classify one Mosquitto log line."""

    if "disconnected: not authorised" in line.lower():
        match = re.search(r"Client (\S+)", line)
        return SecurityEvent(
            event_type="authentication_failure",
            message=line.strip(),
            client_id=match.group(1) if match else None,
        )

    if (
        "openssl error" in line.lower()
        or "protocol error" in line.lower()
    ):
        return SecurityEvent(
            event_type="tls_failure",
            message=line.strip(),
        )

    if "New connection from" in line:
        return SecurityEvent(
            event_type="connection_attempt",
            message=line.strip(),
        )

    return None


def record_security_event(line: str):
    """Parse and record a Mosquitto log event."""
    from time import time

    from metrics import (
        MQTT_SECURITY_EVENTS,
        MQTT_SECURITY_LAST_EVENT_TIMESTAMP,
    )

    event = parse_security_event(line)

    if event is None:
        return None

    MQTT_SECURITY_EVENTS.labels(
        event_type=event.event_type
    ).inc()

    MQTT_SECURITY_LAST_EVENT_TIMESTAMP.set(time())

    return event


def follow_security_log(log_path, poll_interval=1.0, stop_event=None):
    """Continuously process complete Mosquitto log lines."""
    import os
    import time

    from metrics import MQTT_SECURITY_MONITOR_ERRORS

    current_inode = None
    position = 0
    initialized = False

    while stop_event is None or not stop_event.is_set():
        try:
            with open(
                log_path,
                "r",
                encoding="utf-8",
                errors="replace",
            ) as log_file:

                # Read metadata from the file actually opened.
                stat = os.fstat(log_file.fileno())
                file_identity = (stat.st_dev, stat.st_ino)

                if not initialized:
                    position = stat.st_size
                    current_inode = file_identity
                    initialized = True

                elif file_identity != current_inode:
                    position = 0
                    current_inode = file_identity

                elif stat.st_size < position:
                    position = 0

                log_file.seek(position)

                while True:
                    line_start = log_file.tell()
                    line = log_file.readline()

                    if not line:
                        break

                    if not line.endswith("\n"):
                        log_file.seek(line_start)
                        break

                    record_security_event(line)

                position = log_file.tell()

        except FileNotFoundError:
            # A newly created file should be read from the start.
            initialized = True
            current_inode = None
            position = 0

        except (OSError, UnicodeError):
            MQTT_SECURITY_MONITOR_ERRORS.inc()

        if stop_event is not None:
            stop_event.wait(poll_interval)
        else:
            time.sleep(poll_interval)


def main():
    import os

    from metrics import start_metrics_server

    log_path = os.getenv(
        "MQTT_SECURITY_LOG_PATH",
        "/logs/security.log",
    )

    metrics_port = int(
        os.getenv("METRICS_PORT", "8001")
    )

    start_metrics_server(metrics_port)

    print(
        f"MQTT Security Monitor started: "
        f"log={log_path}, metrics_port={metrics_port}",
        flush=True,
    )

    follow_security_log(log_path)


if __name__ == "__main__":
    main()
