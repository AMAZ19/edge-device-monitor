"""Security hardening tests for MQTT TLS."""

import ssl
from unittest.mock import MagicMock

import pytest

from mqtt_security import (
    configure_mqtt_client,
    create_tls_context,
    get_mqtt_credentials,
    get_mqtt_port,
    tls_enabled,
)


def test_tls_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MQTT_TLS_ENABLED", raising=False)
    assert tls_enabled() is False


def test_invalid_tls_setting_rejected(monkeypatch):
    monkeypatch.setenv("MQTT_TLS_ENABLED", "invalid")

    with pytest.raises(ValueError):
        tls_enabled()


def test_tls_requires_ca_certificate(monkeypatch):
    monkeypatch.setenv("MQTT_TLS_ENABLED", "true")
    monkeypatch.delenv("MQTT_CA_CERT", raising=False)

    with pytest.raises(ValueError):
        create_tls_context()


def test_missing_ca_certificate_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("MQTT_TLS_ENABLED", "true")
    monkeypatch.setenv(
        "MQTT_CA_CERT",
        str(tmp_path / "missing-ca.crt"),
    )

    with pytest.raises(FileNotFoundError):
        create_tls_context()


def test_tls_context_enforces_certificate_validation(
    monkeypatch, tmp_path
):
    import subprocess

    cert_path = tmp_path / "ca.crt"
    key_path = tmp_path / "ca.key"

    subprocess.run(
        [
            "openssl", "req", "-x509",
            "-newkey", "rsa:2048",
            "-nodes",
            "-keyout", str(key_path),
            "-out", str(cert_path),
            "-days", "30",
            "-subj", "/CN=Test-CA",
        ],
        check=True,
        capture_output=True,
    )

    monkeypatch.setenv("MQTT_TLS_ENABLED", "true")
    monkeypatch.setenv("MQTT_CA_CERT", str(cert_path))

    context = create_tls_context()

    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    assert context.minimum_version >= ssl.TLSVersion.TLSv1_2


def test_mqtt_client_receives_tls_context(monkeypatch):
    monkeypatch.setenv("MQTT_TLS_ENABLED", "true")

    context = ssl.create_default_context()
    monkeypatch.setattr(
        "mqtt_security.create_tls_context",
        lambda: context,
    )

    client = MagicMock()

    result = configure_mqtt_client(client)

    client.tls_set_context.assert_called_once_with(context)
    assert result is client


@pytest.mark.parametrize("port", ["0", "65536", "-1"])
def test_invalid_mqtt_ports_rejected(monkeypatch, port):
    monkeypatch.setenv("MQTT_TLS_ENABLED", "true")
    monkeypatch.setenv("MQTT_PORT", port)

    with pytest.raises(ValueError):
        get_mqtt_port()


def test_missing_password_file_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("MQTT_USERNAME", "iot_test")
    monkeypatch.setenv(
        "MQTT_PASSWORD_FILE",
        str(tmp_path / "missing-password"),
    )

    with pytest.raises(FileNotFoundError):
        get_mqtt_credentials()


def test_empty_password_rejected(monkeypatch, tmp_path):
    password_file = tmp_path / "password.txt"
    password_file.write_text("")

    monkeypatch.setenv("MQTT_USERNAME", "iot_test")
    monkeypatch.setenv("MQTT_PASSWORD_FILE", str(password_file))

    with pytest.raises(ValueError):
        get_mqtt_credentials()
