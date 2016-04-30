#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import time
import datetime
import logging
import requests
import paho.mqtt.client as mqtt # sudo pip install paho-mqtt
import sys
import socket
#sys.path.append("/home/pi/Source/GrovePi/Software/Python/")
from grovepi import grovepi
import traceback

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

# Example of sensor connected to Raspberry Pi pin 23
GROVE_SENSOR = 2

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 600

MQTT_CLIENTID = socket.gethostname() + '_temp_pub'
MQTT_TOPIC = 'home/sensor/temperature/' + socket.gethostname()

FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = '/var/log/mqtt_client.log'
logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('My_Temperature_mqtt')

def json_Payload():
	# Attempt to get sensor reading.
	[temp,humidity] = grovepi.dht(GROVE_SENSOR,0)

	# Skip to the next reading if a valid measurement couldn't be taken.
	# This might happen if the CPU is under a lot of load and the sensor
	# can't be reliably read (timing is critical to read the sensor).
	if humidity is None or temp is None:
		raise ValueError('Sensor reading failed')

	payload = "{ " + '"Temperature": "{0:0.1f} C"'.format(temp) + ', "Humidity": "{0:0.1f} %"'.format(humidity) + " }"
	logger.info(os.path.basename(__file__) + " - payload: %s" % payload)
	return payload
 
def on_connected(client, userdata, rc):
	logger.info(os.path.basename(__file__) + " - mqtt connected")

def on_message(mosq, obj, msg):
    global message
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    message = msg.payload

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)


mqttc = mqtt.Client(MQTT_CLIENTID)
mqttc.on_connect = on_connected
mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

mqttc.connect('wasabi', 1883)
mqttc.loop_start()	
while mqttc.loop() == 0:
	try:
		mqttc.publish(MQTT_TOPIC, json_Payload(), qos = 1, retain = 1)
		time.sleep(10)# sleep for 10 seconds before next call
	except ValueError as err:
		# we just don't publish bad readings
		#print(err.args)
		logger.warning(os.path.basename(__file__) + " - %s " % err.args)
		time.sleep(5)
