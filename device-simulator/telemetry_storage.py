import sqlite3
from pathlib import Path
from contextlib import closing

DATABASE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "telemetry.db"
)


def initialize_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                motor_current REAL NOT NULL,
                operating_hours REAL NOT NULL
            )
        """)

def save_telemetry(device):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        connection.execute("""
            INSERT INTO telemetry (
                device_id,
                timestamp,
                temperature,
                humidity,
                motor_current,
                operating_hours
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            device["device_id"],
            device["timestamp"],
            device["temperature"],
            device["humidity"],
            device["motor_current"],
            device["operating_hours"],
        ))

def get_latest_telemetry(limit=10, device_id=None):
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("limit must be a positive integer")

    if limit <= 0:
        raise ValueError("limit must be a positive integer")

    if device_id is not None:
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("device_id must be a non-empty string")

    query = """
        SELECT
            id,
            device_id,
            timestamp,
            temperature,
            humidity,
            motor_current,
            operating_hours
        FROM telemetry
    """
    parameters = []

    if device_id is not None:
        query += " WHERE device_id = ?"
        parameters.append(device_id)

    query += " ORDER BY id DESC LIMIT ?"
    parameters.append(limit)

    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, parameters).fetchall()

        return [dict(row) for row in rows]

def get_temperature_statistics(device_id=None):
    if device_id is not None:
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("device_id must be a non-empty string")

    query = """
        SELECT
            COUNT(*) AS measurement_count,
            MIN(temperature) AS min_temperature,
            AVG(temperature) AS avg_temperature,
            MAX(temperature) AS max_temperature
        FROM telemetry
    """
    parameters = []

    if device_id is not None:
        query += " WHERE device_id = ?"
        parameters.append(device_id)

    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(query, parameters).fetchone()

        return dict(row)
