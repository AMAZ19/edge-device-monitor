from mqtt_consumer import validate_sensor_value


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
