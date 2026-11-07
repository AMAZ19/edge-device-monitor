
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def save_telemetry(device):
    query = """
        INSERT INTO telemetry (
            device_id,
            timestamp,
            temperature,
            humidity,
            motor_current,
            operating_hours
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        device["device_id"],
        device["timestamp"],
        device["temperature"],
        device["humidity"],
        device["motor_current"],
        device["operating_hours"],
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
