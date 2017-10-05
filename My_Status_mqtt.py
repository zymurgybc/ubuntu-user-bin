#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os
from subprocess import check_output
import time
import datetime
import logging
import requests
import paho.mqtt.client as mqtt # sudo pip install paho-mqtt
import sys
import socket
import traceback

import json
config_json = os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.json'
with open(config_json, 'r') as f:
    config = json.load(f)

FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = config["mqtt_client_log"]
logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('My_Status_mqtt')

def on_connected(client, userdata, rc):
     logger.info(os.path.basename(__file__) + " - mqtt connected")
     publish_status(client)

#def on_message(mosq, obj, msg):
#    global message
#    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
#    message = msg.payload

def on_publish(mosq, obj, mid):
    logger.info(os.path.basename(__file__) + " - Published: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    logger.info(os.path.basename(__file__) + " - Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    logger.info(os.path.basename(__file__) + " - Log: " + string)


def getIP():
    return check_output(["hostname", "--all-ip-addresses"])

def publish_status(client):
    my_status =  'connected ' + getIP() 
    logger.info(os.path.basename(__file__) + " - Sending: " + my_status)
    client.publish(MQTT_TOPIC, my_status, qos = 1, retain = 1)

MQTT_CLIENTID = socket.gethostname() + '_temp_pub'
MQTT_TOPIC = 'home/client/' + socket.gethostname() + '/status'

mqttc = mqtt.Client(MQTT_CLIENTID)
mqttc.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
mqttc.will_set(MQTT_TOPIC, payload='disconnected', qos=0, retain=True)

mqttc.on_connect = on_connected
#mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

while True:
    logger.info(os.path.basename(__file__) + " - Attempting connection")
    # cast the port from 'unicode' to plain 'string'
    mqttc.connect(config["mqtt_host"], str(config["mqtt_port"]))
    mqttc.loop_start()
    client_loop = mqttc.loop(120)
    while client_loop == 0:
        try:
            publish_status(mqttc)
            time.sleep(60)   # sleep for 30 seconds before next call
            client_loop = mqttc.loop(.25) # blocks for 250ms
        except ValueError as err1:
            # we just don't publish bad readings
            logger.warning(os.path.basename(__file__) + " - [2] %s " % err.args)
            time.sleep(5)

    logger.info(os.path.basename(__file__) + " - exiting with %s" % str(client_loop))

#except Exception as err2:
#    logger.warning(os.path.basename(__file__) + " - [1] %s " % err.args)
