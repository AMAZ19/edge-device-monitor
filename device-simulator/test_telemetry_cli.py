import json
import sys

import pytest

import telemetry_cli
import telemetry_storage


@pytest.fixture
def cli_database(tmp_path, monkeypatch):
    database_path = tmp_path / "telemetry.db"
    monkeypatch.setattr(
        telemetry_storage, "DATABASE_PATH", database_path
    )
    telemetry_storage.initialize_database()

    for device_id, temperature in [
        ("device-a", 24.0),
        ("device-b", 25.0),
        ("device-a", 26.0),
    ]:
        telemetry_storage.save_telemetry({
            "device_id": device_id,
            "timestamp": "2026-11-04T18:00:00+00:00",
            "temperature": temperature,
            "humidity": 50.0,
            "motor_current": 1.5,
            "operating_hours": 0.1,
        })

    return database_path


def test_cli_latest(cli_database, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        [
            "telemetry_cli.py", "latest",
            "--limit", "1",
            "--device-id", "device-a",
        ],
    )

    telemetry_cli.main()

    output = capsys.readouterr()
    rows = json.loads(output.out)

    assert output.err == ""
    assert len(rows) == 1
    assert rows[0]["id"] == 3
    assert rows[0]["device_id"] == "device-a"
    assert rows[0]["temperature"] == 26.0


def test_cli_stats(cli_database, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        [
            "telemetry_cli.py", "stats",
            "--device-id", "device-a",
        ],
    )

    telemetry_cli.main()

    output = capsys.readouterr()
    result = json.loads(output.out)

    assert output.err == ""
    assert result == {
        "measurement_count": 2,
        "min_temperature": 24.0,
        "avg_temperature": 25.0,
        "max_temperature": 26.0,
    }

@pytest.mark.parametrize(
    "arguments, expected_message",
    [
        (
            ["latest", "--limit", "0"],
            "limit must be a positive integer",
        ),
        (
            ["latest", "--limit", "abc"],
            "invalid int value",
        ),
        (
            ["latest", "--device-id", "   "],
            "device_id must be a non-empty string",
        ),
        (
            ["stats", "--device-id", ""],
            "device_id must be a non-empty string",
        ),
        (
            [],
            "the following arguments are required",
        ),
        (
            ["unknown"],
            "invalid choice",
        ),
    ],
)
def test_cli_invalid_arguments(
    monkeypatch, capsys, arguments, expected_message
):
    monkeypatch.setattr(
        sys, "argv", ["telemetry_cli.py", *arguments]
    )

    with pytest.raises(SystemExit) as error:
        telemetry_cli.main()

    output = capsys.readouterr()

    assert error.value.code == 2
    assert output.out == ""
    assert expected_message in output.err


def test_cli_database_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        telemetry_storage,
        "DATABASE_PATH",
        tmp_path / "missing-directory" / "telemetry.db",
    )
    monkeypatch.setattr(
        sys, "argv", ["telemetry_cli.py", "latest"]
    )

    with pytest.raises(SystemExit) as error:
        telemetry_cli.main()

    output = capsys.readouterr()

    assert error.value.code == 1
    assert output.out == ""
    assert "Database error:" in output.err
