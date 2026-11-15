#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

CERT_DIR="$PWD/docker/mosquitto/certs"
ROTATION_DIR="/tmp/iot-cert-rotation"
BACKUP_DIR="$ROTATION_DIR/backup"

NETWORK=$(docker inspect \
  "$(docker compose ps -q mosquitto)" \
  --format '{{range $name, $config := .NetworkSettings.Networks}}{{$name}}{{"\n"}}{{end}}' \
  | head -n 1)

if [[ -z "$NETWORK" ]]; then
  echo "ERROR: Docker network not found"
  exit 1
fi

echo "===== 1. Preconditions ====="

sudo test -s "$BACKUP_DIR/server.crt"
sudo test -s "$BACKUP_DIR/server.key"
sudo test -s "$ROTATION_DIR/server-new.crt"
sudo test -s "$ROTATION_DIR/server-new.key"

sudo openssl verify \
  -CAfile "$CERT_DIR/ca.crt" \
  "$ROTATION_DIR/server-new.crt"

sudo openssl x509 \
  -in "$ROTATION_DIR/server-new.crt" \
  -checkend 2592000 -noout

verify_pair() {
  local cert="$1"
  local key="$2"
  local cert_hash key_hash

  cert_hash=$(sudo openssl x509 -in "$cert" \
    -pubkey -noout |
    openssl pkey -pubin -outform DER |
    sha256sum | cut -d' ' -f1)

  key_hash=$(sudo openssl pkey -in "$key" \
    -pubout -outform DER |
    sha256sum | cut -d' ' -f1)

  [[ "$cert_hash" == "$key_hash" ]]
}

verify_pair \
  "$ROTATION_DIR/server-new.crt" \
  "$ROTATION_DIR/server-new.key"

verify_pair \
  "$BACKUP_DIR/server.crt" \
  "$BACKUP_DIR/server.key"

echo "PASS: Certificate preconditions"

rollback() {
  echo "===== ROLLBACK ====="

  sudo install -o 1883 -g 1883 -m 600 \
    "$BACKUP_DIR/server.key" \
    "$CERT_DIR/server.key"

  sudo install -o 1883 -g 1883 -m 644 \
    "$BACKUP_DIR/server.crt" \
    "$CERT_DIR/server.crt"

  docker compose restart mosquitto

  echo "Rollback completed"
}


echo "===== 2. Prepare rollback protection ====="

ROTATION_STARTED=false
ROLLBACK_RUNNING=false

rollback() {
  if [[ "$ROLLBACK_RUNNING" == true ]]; then
    return 1
  fi

  ROLLBACK_RUNNING=true
  trap - ERR INT TERM

  echo "===== AUTOMATIC ROLLBACK ====="

  local failed=0

  sudo install -o 1883 -g 1883 -m 600 \
    "$BACKUP_DIR/server.key" \
    "$CERT_DIR/server.key" || failed=1

  sudo install -o 1883 -g 1883 -m 644 \
    "$BACKUP_DIR/server.crt" \
    "$CERT_DIR/server.crt" || failed=1

  docker compose restart mosquitto || failed=1

  if [[ "$failed" -ne 0 ]]; then
    echo "CRITICAL: Automatic rollback failed"
    return 1
  fi

  echo "Rollback files restored; broker restarted."
}

on_error() {
  local exit_code=${1:-$?}
  trap - ERR INT TERM

  if [[ "$ROTATION_STARTED" == true ]]; then
    rollback || echo "CRITICAL: Manual recovery required"
  fi

  exit "$exit_code"
}

trap on_error ERR
trap 'on_error 130' INT
trap 'on_error 143' TERM

echo "===== 3. Activate new certificate ====="

ROTATION_STARTED=true

sudo install -o 1883 -g 1883 -m 600 \
  "$ROTATION_DIR/server-new.key" \
  "$CERT_DIR/server.key"

sudo install -o 1883 -g 1883 -m 644 \
  "$ROTATION_DIR/server-new.crt" \
  "$CERT_DIR/server.crt"

echo "===== 4. Restart Mosquitto ====="

docker compose restart mosquitto

echo "===== 5. Verify live TLS certificate ====="

EXPECTED_FINGERPRINT=$(sudo openssl x509 \
  -in "$ROTATION_DIR/server-new.crt" \
  -outform DER | sha256sum | cut -d' ' -f1)

TLS_READY=false

for attempt in 1 2 3 4 5; do
  if TLS_OUTPUT=$(docker run --rm \
    --network "$NETWORK" \
    -v "$CERT_DIR/ca.crt:/certs/ca.crt:ro" \
    alpine/openssl \
    s_client \
    -connect mosquitto:8883 \
    -servername mosquitto \
    -CAfile /certs/ca.crt \
    -verify_hostname mosquitto \
    -verify_return_error \
    -showcerts </dev/null 2>&1); then
    TLS_READY=true
    break
  fi

  echo "TLS not ready, attempt $attempt/5"
  sleep 2
done

if [[ "$TLS_READY" != true ]]; then
  echo "ERROR: TLS handshake failed after 5 attempts"
  false
fi

if [[ "$TLS_OUTPUT" != *"Verification: OK"* ]]; then
  echo "ERROR: TLS certificate verification failed"
  false
fi

LIVE_CERT=$(printf '%s\n' "$TLS_OUTPUT" |
  sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p')

LIVE_FINGERPRINT=$(printf '%s\n' "$LIVE_CERT" |
  openssl x509 -outform DER |
  sha256sum | cut -d' ' -f1)

if [[ "$EXPECTED_FINGERPRINT" != "$LIVE_FINGERPRINT" ]]; then
  echo "ERROR: Broker is not serving the new certificate"
  false
fi

echo "PASS: Broker serves the new certificate"

echo "===== 6. Final broker status ====="

docker compose ps mosquitto

trap - ERR INT TERM
ROTATION_STARTED=false

echo "PASS: MQTT certificate rotation completed"
