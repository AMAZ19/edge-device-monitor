from mqtt_consumer import validate_sensor_value
import pytest
from types import SimpleNamespace
from mqtt_consumer import validate_sensor_value, on_message

def test_valid_temperature():
    result, reason = validate_sensor_value(25, 20, 30)

    assert result is True
    assert reason == "Valid"

def test_temperature_out_of_range():
    result, reason = validate_sensor_value(35, 20, 30)

    assert result is False
    assert reason == "Out of range"

def test_invalid_temperature_data_type():
    result, reason = validate_sensor_value("warm", 20, 30)

    assert result is False
    assert reason == "Invalid data type"

def test_temperature_lower_boundary():
    result, reason = validate_sensor_value(20, 20, 30)

    assert result is True
    assert reason == "Valid"

def test_temperature_upper_boundary():
    result, reason = validate_sensor_value(30, 20, 30)

    assert result is True
    assert reason == "Valid"

def test_temperature_boolean_value():
    result, reason = validate_sensor_value(True, 20, 30)

    assert result is False
    assert reason == "Invalid data type"

@pytest.mark.parametrize(
    "temperature, expected",
    [
        (20, True),
        (25, True),
        (30, True),
        (19, False),
        (31, False),
    ]
)
def test_temperature_parameterized(temperature, expected):
    result, reason = validate_sensor_value(temperature, 20, 30)

    assert result is expected

def test_on_message_valid_data(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"device_id":"test-001","temperature":25,"humidity":50,"motor_current":1.5}'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Temperature validation: PASSED" in output
    assert "Humidity validation: PASSED" in output
    assert "Motor Current validation: PASSED" in output

def test_on_message_invalid_json(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"temperature":25,'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Invalid sensor data:" in output

def test_on_message_invalid_temperature(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"device_id":"test-004","temperature":35,"humidity":50,"motor_current":1.5}'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Temperature validation: FAILED - Out of range" in output
    assert "Humidity validation: PASSED" in output
    assert "Motor Current validation: PASSED" in output

def test_on_message_invalid_humidity(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"device_id":"test-005","temperature":25,"humidity":75,"motor_current":1.5}'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Temperature validation: PASSED" in output
    assert "Humidity validation: FAILED - Out of range" in output
    assert "Motor Current validation: PASSED" in output

def test_on_message_invalid_humidity(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"device_id":"test-005","temperature":25,"humidity":75,"motor_current":1.5}'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Temperature validation: PASSED" in output
    assert "Humidity validation: FAILED - Out of range" in output
    assert "Motor Current validation: PASSED" in output


def test_on_message_invalid_motor_current(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"device_id":"test-006","temperature":25,"humidity":50,"motor_current":3.5}'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Temperature validation: PASSED" in output
    assert "Humidity validation: PASSED" in output
    assert "Motor Current validation: FAILED - Out of range" in output


def test_on_message_invalid_all_sensors(capsys):
    message = SimpleNamespace(
        topic="iot/device/telemetry",
        payload=b'{"device_id":"test-007","temperature":35,"humidity":75,"motor_current":3.5}'
    )

    on_message(None, None, message)

    output = capsys.readouterr().out

    assert "Temperature validation: FAILED - Out of range" in output
    assert "Humidity validation: FAILED - Out of range" in output
    assert "Motor Current validation: FAILED - Out of range" in output
