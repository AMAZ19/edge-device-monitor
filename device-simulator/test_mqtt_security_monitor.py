from mqtt_security_monitor import parse_security_event


def test_authentication_failure():
    line = (
        "Client auto-123 [172.18.0.9:37038] "
        "disconnected: not authorised."
    )

    event = parse_security_event(line)

    assert event is not None
    assert event.event_type == "authentication_failure"
    assert event.client_id == "auto-123"


def test_tls_failure():
    event = parse_security_event(
        "OpenSSL Error: handshake failed"
    )

    assert event is not None
    assert event.event_type == "tls_failure"


def test_connection_attempt():
    event = parse_security_event(
        "New connection from 172.18.0.9:37038 on port 8883."
    )

    assert event is not None
    assert event.event_type == "connection_attempt"


def test_normal_message_ignored():
    event = parse_security_event(
        "mosquitto version 2.1.2 running"
    )

    assert event is None
