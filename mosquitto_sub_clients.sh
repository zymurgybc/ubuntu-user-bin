#!/bin/bash
mosquitto_sub -d -v -p 1883    \
              -h 192.168.1.50  \
              -t home/client/#     \
              -u $HOSTNAME     \
              --pw itsasecret  \
              --will-topic clients/$HOSTNAME/status  \
              --will-payload disconnected \
              --will-qos 1                \
              --will-retain


