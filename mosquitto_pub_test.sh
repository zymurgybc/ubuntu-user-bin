#!/bin/bash
CERT_FOLDER="${HOME}/.openssl"
CA_CERT="${CERT_FOLDER}/ca-chain.cert.pem"
MQTT_KEY="${CERT_FOLDER}/`hostname`.mqtt-client.key.pem"
MQTT_CERT="${CERT_FOLDER}/`hostname`.mqtt-client.cert.pem"

if [ ! -f "$CA_CERT" ]; then
	echo File $CA_CERT does not exist
fi

if [ ! -f "$MQTT_KEY" ]; then
	echo File $MQTT_KEY does not exist
fi

if [ ! -f "$MQTT_CERT" ]; then
	echo File $MQTT_CERT does not exist
fi

mosquitto_pub -d \
              -h 192.168.1.50 \
              -p 8883 \
              -u `hostname`        \
              -P itsasecret        \
              -t /test/`hostname`   \
              -m test              \
              --will-topic test/`hostname` \
              --will-payload Disconnected \
              --cert $MQTT_CERT    \
              --key  $MQTT_KEY     \
              --cafile $CA_CERT    \
              --tls-version tlsv1.2
