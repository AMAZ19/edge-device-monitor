#!/bin/bash

HOSTNAME=$(hostname)

#uptime 

#free -h

#df -h /


IP_ADDRESS=$(ip addr | grep "inet " | grep -v "127.0.0.1" | awk  '{print $2}' | cut -d/ -f1)

TIMESTAMP=$(date --iso-8601=seconds)
{
echo "{"
echo " \"hostname\": \"$HOSTNAME\","
echo " \"ip_address\": \"$IP_ADDRESS\","
echo " \"timestamp\": \"$TIMESTAMP\""
echo "}"
} > ../data/device_status.json

echo "$TIMESTAMP | $HOSTNAME | $IP_ADDRESS" >> ../logs/device_status.log
mosquitto_pub -h localhost -t "iot/device/status" -r -f ../data/device_status.json

