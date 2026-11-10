
import json
import logging
import os

from flask import Flask, jsonify, request
import paho.mqtt.publish as publish

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = "iot/device/alerts"
WEBHOOK_TOKEN = os.getenv("GRAFANA_WEBHOOK_TOKEN", "")


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/grafana-alert")
def grafana_alert():
    if not WEBHOOK_TOKEN:
        return jsonify({"error": "Webhook token not configured"}), 503

    if not (
        request.headers.get("X-Webhook-Token") == WEBHOOK_TOKEN
        or request.headers.get("Authorization") == f"Bearer {WEBHOOK_TOKEN}"
    ):
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    if not isinstance(payload.get("alerts"), list):
        return jsonify({"error": "Missing alerts array"}), 400

    message = {
        "source": "grafana",
        "status": payload.get("status", "unknown"),
        "receiver": payload.get("receiver", ""),
        "alerts": payload["alerts"],
    }

    try:
        publish.single(
            topic=MQTT_TOPIC,
            payload=json.dumps(message),
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            qos=1,
            retain=False,
        )
    except Exception:
        app.logger.exception("MQTT publish failed")
        return jsonify({"error": "MQTT publish failed"}), 502

    app.logger.info(
        "Published %d alert(s) to %s",
        len(message["alerts"]),
        MQTT_TOPIC,
    )

    return jsonify({"status": "published"}), 200


if __name__ == "__main__":
    if not WEBHOOK_TOKEN:
        raise SystemExit("GRAFANA_WEBHOOK_TOKEN is required")

    app.run(host="0.0.0.0", port=5000, debug=False)
