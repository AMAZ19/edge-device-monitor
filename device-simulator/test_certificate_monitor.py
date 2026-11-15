"""Tests for MQTT certificate expiration monitoring."""

from datetime import datetime, timedelta, timezone

import pytest

import certificate_monitor


def test_valid_certificate(monkeypatch):
    expiry = datetime.now(timezone.utc) + timedelta(days=365)

    monkeypatch.setattr(
        certificate_monitor,
        "get_certificate_expiry",
        lambda _: expiry,
    )

    status, days, _ = certificate_monitor.check_certificate(
        "test.crt"
    )

    assert status == "OK"
    assert days > 364


def test_certificate_expiring_soon(monkeypatch):
    expiry = datetime.now(timezone.utc) + timedelta(days=10)

    monkeypatch.setattr(
        certificate_monitor,
        "get_certificate_expiry",
        lambda _: expiry,
    )

    status, days, _ = certificate_monitor.check_certificate(
        "test.crt"
    )

    assert status == "WARNING"
    assert 9 < days <= 10


def test_expired_certificate(monkeypatch):
    expiry = datetime.now(timezone.utc) - timedelta(days=1)

    monkeypatch.setattr(
        certificate_monitor,
        "get_certificate_expiry",
        lambda _: expiry,
    )

    status, days, _ = certificate_monitor.check_certificate(
        "test.crt"
    )

    assert status == "EXPIRED"
    assert days < 0


def test_custom_warning_threshold(monkeypatch):
    expiry = datetime.now(timezone.utc) + timedelta(days=60)

    monkeypatch.setattr(
        certificate_monitor,
        "get_certificate_expiry",
        lambda _: expiry,
    )

    status, _, _ = certificate_monitor.check_certificate(
        "test.crt",
        warning_days=90,
    )

    assert status == "WARNING"


def test_negative_warning_threshold_rejected():
    with pytest.raises(ValueError):
        certificate_monitor.check_certificate(
            "test.crt",
            warning_days=-1,
        )


def test_missing_certificate_rejected(tmp_path):
    missing = tmp_path / "missing.crt"

    with pytest.raises(FileNotFoundError):
        certificate_monitor.get_certificate_expiry(missing)


def test_generated_certificate(tmp_path):
    import subprocess

    cert_path = tmp_path / "test.crt"
    key_path = tmp_path / "test.key"

    subprocess.run(
        [
            "openssl", "req", "-x509",
            "-newkey", "rsa:2048",
            "-nodes",
            "-keyout", str(key_path),
            "-out", str(cert_path),
            "-days", "30",
            "-subj", "/CN=test.local",
        ],
        check=True,
        capture_output=True,
    )

    expiry = certificate_monitor.get_certificate_expiry(cert_path)

    assert expiry.tzinfo == timezone.utc
    assert expiry > datetime.now(timezone.utc)
