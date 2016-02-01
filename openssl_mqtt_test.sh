#!/bin/bash

CA_CERT=$HOME/.openssl/ca-chain.cert.pem
MQTT_KEY=$HOME/.openssl/`hostname`.mqtt-client.key.pem
MQTT_CERT=$HOME/.openssl/`hostname`.mqtt-client.cert.pem

if [ ! -f $CA_CERT ]; then
	echo File $CA_CERT does not exist
fi

if [ ! -f $MQTT_KEY ]; then
	echo File $MQTT_KEY does not exist
fi

if [ ! -f $CA_CERT ]; then
	echo File $MQTT_CERT does not exist
fi

openssl s_client \
    -showcerts \
    -connect  192.168.1.50:8883 \
    -cert $MQTT_CERT \
    -key  $MQTT_KEY  \
    -CAfile   $CA_CERT 
