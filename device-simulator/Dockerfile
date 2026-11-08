FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY device_simulator.py .
COPY mqtt_consumer.py .
COPY metrics.py .
COPY telemetry_storage.py .
COPY postgres_storage.py .

ENV PYTHONUNBUFFERED=1
ENV MQTT_HOST=localhost
ENV MQTT_PORT=1883
ENV MEASUREMENT_INTERVAL=5

CMD ["python", "device_simulator.py"]
