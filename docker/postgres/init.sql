CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    motor_current DOUBLE PRECISION NOT NULL,
    operating_hours DOUBLE PRECISION NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_telemetry_device_time
ON telemetry (device_id, timestamp);
