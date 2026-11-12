FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Unprivilegierten Benutzer erstellen
RUN addgroup -S appgroup \
    && adduser -S -G appgroup -h /app appuser

COPY --chown=appuser:appgroup device_simulator.py .
COPY --chown=appuser:appgroup mqtt_consumer.py .
COPY --chown=appuser:appgroup metrics.py .
COPY --chown=appuser:appgroup telemetry_storage.py .
COPY --chown=appuser:appgroup postgres_storage.py .

# Schreibzugriff auf /app für SQLite und andere
# lokale Dateien sicherstellen
RUN chown appuser:appgroup /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV MQTT_HOST=localhost
ENV MQTT_PORT=1883
ENV MEASUREMENT_INTERVAL=5

CMD ["python", "device_simulator.py"]
