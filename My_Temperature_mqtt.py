#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import time
import datetime
import requests
import paho.mqtt.client as mqttimport sys
import socket

import Adafruit_DHT
import traceback

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT11

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = 5
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 600


mqttc = mqtt.Client(socket.gethostname() + "_temp_pub")
mqttc.connect("wasabi", 1883)
mqttc.publish("home/" + socket.gethostname() + "/downstairs/temperature", json_string())
mqttc.loop(FREQUENCY_SECONDS) //timeout = 2s

def json_string()
	# Attempt to get sensor reading.
	humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

	# Skip to the next reading if a valid measurement couldn't be taken.
	# This might happen if the CPU is under a lot of load and the sensor
	# can't be reliably read (timing is critical to read the sensor).
	if humidity is None or temp is None:
		time.sleep(2)
		#continue
		exit(1)

	return '{ Temperature: {0:0.1f} C'.format(temp) + ', Humidity:    {0:0.1f} %'.format(humidity) + '}'
 
