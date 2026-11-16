#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="${MQTT_CI_TEST_DIR:-/tmp/iot-mqtt-ci}"
CERT_DIR="$TEST_DIR/certs"
AUTH_DIR="$TEST_DIR/auth"
SECRET_DIR="$TEST_DIR/secrets"

mkdir -p "$CERT_DIR" "$AUTH_DIR" "$SECRET_DIR"
chmod 755 "$TEST_DIR" "$CERT_DIR" "$AUTH_DIR"
chmod 700 "$SECRET_DIR"

echo "===== Generate temporary CA ====="

openssl req -x509 -newkey rsa:3072 -nodes \
  -keyout "$CERT_DIR/ca.key" \
  -out "$CERT_DIR/ca.crt" \
  -days 2 \
  -subj "/CN=IoT-CI-Test-CA" \
  >/dev/null 2>&1

echo "===== Generate MQTT server certificate ====="

openssl req -newkey rsa:3072 -nodes \
  -keyout "$CERT_DIR/server.key" \
  -out "$TEST_DIR/server.csr" \
  -subj "/CN=mosquitto" \
  >/dev/null 2>&1

cat > "$TEST_DIR/server.ext" <<'EXT'
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:mosquitto,DNS:localhost,IP:127.0.0.1
EXT

openssl x509 -req \
  -in "$TEST_DIR/server.csr" \
  -CA "$CERT_DIR/ca.crt" \
  -CAkey "$CERT_DIR/ca.key" \
  -CAcreateserial \
  -out "$CERT_DIR/server.crt" \
  -days 2 -sha256 \
  -extfile "$TEST_DIR/server.ext" \
  >/dev/null 2>&1

echo "===== Generate temporary MQTT credentials ====="

MQTT_PASSWORD="$(openssl rand -hex 24)"
printf '%s\n' "$MQTT_PASSWORD" \
  > "$SECRET_DIR/iot_simulator.txt"

rm -f -- "$AUTH_DIR/passwords"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  --entrypoint mosquitto_passwd \
  -v "$AUTH_DIR:/auth" \
  eclipse-mosquitto:2 \
  -b -c /auth/passwords \
  iot_simulator "$MQTT_PASSWORD"

echo "===== Write secure broker configuration ====="

cat > "$TEST_DIR/mosquitto.conf" <<'CONF'
listener 8883 0.0.0.0
listener_allow_anonymous false
password_file /mosquitto/auth/passwords

cafile /mosquitto/certs/ca.crt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key

tls_version tlsv1.2
CONF

chmod 600 "$CERT_DIR/ca.key" "$SECRET_DIR/iot_simulator.txt"
chmod 640 "$CERT_DIR/server.key" "$AUTH_DIR/passwords"
chmod 644 "$CERT_DIR/ca.crt" "$CERT_DIR/server.crt"

# Mosquitto container runs as UID/GID 1883.
docker run --rm --user 0:0 \
  --mount type=bind,src="$CERT_DIR",dst=/certs \
  --mount type=bind,src="$AUTH_DIR",dst=/auth \
  --entrypoint chown \
  eclipse-mosquitto:2 \
  1883:1883 /certs/server.key /auth/passwords

echo "===== Verify generated certificate ====="

openssl verify \
  -CAfile "$CERT_DIR/ca.crt" \
  -purpose sslserver \
  -verify_hostname mosquitto \
  "$CERT_DIR/server.crt"

echo "PASS: Temporary MQTT test materials generated"
