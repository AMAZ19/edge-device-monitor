"""Shared MQTT TLS configuration."""

import os
import ssl
from pathlib import Path


def tls_enabled():
    """Check whether MQTT TLS is enabled."""
    value = os.getenv("MQTT_TLS_ENABLED", "false").lower()

    if value not in ("true", "false"):
        raise ValueError(
            "MQTT_TLS_ENABLED must be true or false"
        )

    return value == "true"


def create_tls_context():
    """Create a secure MQTT TLS context."""
    if not tls_enabled():
        return None

    ca_path = os.getenv("MQTT_CA_CERT")

    if not ca_path:
        raise ValueError(
            "MQTT_CA_CERT is required when TLS is enabled"
        )

    if not Path(ca_path).is_file():
        raise FileNotFoundError(
            f"MQTT CA certificate not found: {ca_path}"
        )

    context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH,
        cafile=ca_path,
    )

    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    return context


def configure_mqtt_client(client):
    """Apply TLS settings to a Paho MQTT client."""
    context = create_tls_context()

    if context is not None:
        client.tls_set_context(context)

    return client


def get_mqtt_port():
    """Return the configured MQTT port."""
    default_port = "8883" if tls_enabled() else "1883"
    port = int(os.getenv("MQTT_PORT", default_port))

    if not 1 <= port <= 65535:
        raise ValueError("Invalid MQTT port")

    return port


def get_mqtt_credentials():
    """Read MQTT credentials from Docker secret files."""
    username = os.getenv("MQTT_USERNAME")
    password_file = os.getenv("MQTT_PASSWORD_FILE")

    if not username and not password_file:
        return None

    if not username or not password_file:
        raise ValueError(
            "MQTT_USERNAME and MQTT_PASSWORD_FILE "
            "must be configured together"
        )

    path = Path(password_file)

    if not path.is_file():
        raise FileNotFoundError(
            f"MQTT password file not found: {password_file}"
        )

    password = path.read_text().rstrip("\r\n")

    if not password:
        raise ValueError("MQTT password must not be empty")

    return username, password


def configure_mqtt_auth(client):
    """Apply MQTT username/password authentication."""
    credentials = get_mqtt_credentials()

    if credentials is not None:
        username, password = credentials
        client.username_pw_set(username, password)

    return client
