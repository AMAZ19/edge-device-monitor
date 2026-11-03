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
