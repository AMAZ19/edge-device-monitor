"""Live MQTT authentication integration tests."""

import os
import socket
import ssl
import threading
import uuid
from pathlib import Path

import paho.mqtt.client as mqtt
import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("MQTT_INTEGRATION_TESTS") != "1",
    reason="Live MQTT integration tests are opt-in",
)


HOST = os.getenv("MQTT_TEST_HOST", "localhost")
PORT = int(os.getenv("MQTT_TEST_PORT", "8883"))
CA_CERT = os.getenv(
    "MQTT_TEST_CA_CERT",
    "docker/mosquitto/certs/ca.crt",
)
USERNAME = os.getenv("MQTT_TEST_USERNAME", "iot_simulator")
PASSWORD_FILE = os.getenv(
    "MQTT_TEST_PASSWORD_FILE",
    "docker/mosquitto/secrets/iot_simulator.txt",
)


def connect_mqtt(username=None, password=None):
    """Connect with TLS and return the MQTT CONNACK code."""
    connected = threading.Event()
    result = {"code": None}

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"security-test-{uuid.uuid4().hex[:12]}",
        protocol=mqtt.MQTTv311,
    )

    context = ssl.create_default_context(
        cafile=str(Path(CA_CERT).resolve())
    )
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    client.tls_set_context(context)

    if username is not None:
        client.username_pw_set(username, password)

    def on_connect(client, userdata, flags, reason_code, properties):
        result["code"] = reason_code
        connected.set()

    client.on_connect = on_connect

    try:
        client.connect(HOST, PORT, keepalive=10)
        client.loop_start()

        if not connected.wait(timeout=5):
            pytest.fail("No MQTT CONNACK received within 5 seconds")

        return result["code"]

    finally:
        client.disconnect()
        client.loop_stop()


def test_anonymous_connection_rejected():
    code = connect_mqtt()
    assert code.is_failure


def test_unknown_username_rejected():
    code = connect_mqtt(
        "unknown_security_test_user",
        "invalid-password",
    )
    assert code.is_failure


def test_wrong_password_rejected():
    code = connect_mqtt(
        USERNAME,
        "intentionally-invalid-password",
    )
    assert code.is_failure


def test_valid_credentials_accepted():
    password = Path(PASSWORD_FILE).read_text().rstrip("\r\n")

    assert password, "Test password must not be empty"

    code = connect_mqtt(USERNAME, password)
    assert not code.is_failure
