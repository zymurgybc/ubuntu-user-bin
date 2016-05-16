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
import traceback

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

MQTT_CLIENTID = socket.gethostname() + '_temp_pub'
MQTT_TOPIC = 'home/client/' + socket.gethostname() + '/status'

FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = '/var/log/mqtt_client.log'
logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('My_Status_mqtt')

def on_connected(client, userdata, rc):
	logger.info(os.path.basename(__file__) + " - mqtt connected")

#def on_message(mosq, obj, msg):
#    global message
#    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
#    message = msg.payload

def on_publish(mosq, obj, mid):
    logger.info(os.path.basename(__file__) + " Published: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    logger.info(os.path.basename(__file__) + " Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    logger.info(os.path.basename(__file__) + "Log: " + string)


mqttc = mqtt.Client(MQTT_CLIENTID)
mqttc.username_pw_set(socket.gethostname(), password='itsasecret')
mqttc.will_set(MQTT_TOPIC, payload='disconnected', qos=0, retain=True)

mqttc.on_connect = on_connected
#mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

mqttc.connect('wasabi', 1883)
mqttc.loop_start()	
while mqttc.loop() == 0:
	try:
		mqttc.publish(MQTT_TOPIC, 'connected', qos = 1, retain = 1)
		time.sleep(30)   # sleep for 30 seconds before next call
	except ValueError as err:
		# we just don't publish bad readings
		logger.warning(os.path.basename(__file__) + " - %s " % err.args)
		time.sleep(5)
