"""Live MQTT TLS security integration tests."""

import os
import socket
import ssl
import subprocess

import pytest


pytestmark = pytest.mark.skipif(
    os.getenv("MQTT_INTEGRATION_TESTS") != "1",
    reason="Live MQTT integration tests are opt-in",
)

HOST = os.getenv("MQTT_TEST_HOST", "mosquitto")
PORT = int(os.getenv("MQTT_TEST_PORT", "8883"))
CA_CERT = os.getenv(
    "MQTT_TEST_CA_CERT",
    "docker/mosquitto/certs/ca.crt",
)


def tls_connect(context, hostname=HOST):
    """Establish a verified TLS connection."""
    with socket.create_connection((HOST, PORT), timeout=5) as sock:
        with context.wrap_socket(
            sock,
            server_hostname=hostname,
        ) as tls_sock:
            return tls_sock.version()


def test_valid_tls_certificate():
    context = ssl.create_default_context(cafile=CA_CERT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    version = tls_connect(context)

    assert version in ("TLSv1.2", "TLSv1.3")


def test_untrusted_ca_rejected(tmp_path):
    key = tmp_path / "untrusted.key"
    cert = tmp_path / "untrusted.crt"

    subprocess.run(
        [
            "openssl", "req", "-x509",
            "-newkey", "rsa:2048",
            "-nodes",
            "-keyout", str(key),
            "-out", str(cert),
            "-days", "1",
            "-subj", "/CN=Untrusted-Test-CA",
        ],
        check=True,
        capture_output=True,
    )

    context = ssl.create_default_context(cafile=str(cert))

    with pytest.raises(ssl.SSLCertVerificationError):
        tls_connect(context)


def test_wrong_hostname_rejected():
    context = ssl.create_default_context(cafile=CA_CERT)

    with pytest.raises(ssl.SSLCertVerificationError):
        tls_connect(
            context,
            hostname="invalid-mqtt-host.example",
        )


def test_plaintext_rejected_on_tls_port():
    with socket.create_connection((HOST, PORT), timeout=5) as sock:
        sock.settimeout(2)
        sock.sendall(
            b"\x10\x0c\x00\x04MQTT\x04\x02\x00\x0a\x00\x00"
        )

        try:
            response = sock.recv(1024)
        except (ConnectionResetError, TimeoutError):
            return

        assert response == b"", (
            "Broker unexpectedly responded to plaintext MQTT"
        )
