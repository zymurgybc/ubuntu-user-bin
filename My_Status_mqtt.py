#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os
from subprocess import check_output
import ctypes
import struct
import time
from datetime import datetime
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

def on_connected(client, userdata, flags, rc):
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
    # in subprocess
    return check_output(["hostname", "--all-ip-addresses"]).decode("utf-8")

def uptime():
    libc = ctypes.CDLL('libc.so.6')
    buf = ctypes.create_string_buffer(4096) # generous buffer to hold
                                            # struct sysinfo
    if libc.sysinfo(buf) != 0:
        print('failed')
        return -1

    uptime = struct.unpack_from('@l', buf.raw)[0]
    return uptime

def myUpdated():
    my_updated = '{{ "DateTime": "{}", "Uptime": "{}" }}'.format(
        time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
        uptime())
    #print( my_updated )
    return my_updated

def publish_status(client):
    my_status =  'connected ' + getIP()
    #print( my_status )
    client.publish(MQTT_STATUS_TOPIC, my_status, qos = 1, retain = 1)
    logger.info(os.path.basename(__file__) + " - Sending status: " + my_status)
    my_updated = myUpdated()
    client.publish(MQTT_UPDATE_TOPIC, my_updated, qos = 1, retain = 1)
    logger.info(os.path.basename(__file__) + " - Sending update: " + my_updated)

MQTT_CLIENTID = socket.gethostname() + '_temp_pub'
MQTT_STATUS_TOPIC = 'home/client/' + socket.gethostname() + '/status'
MQTT_UPDATE_TOPIC = 'home/client/' + socket.gethostname() + '/updated'

mqttc = mqtt.Client(MQTT_CLIENTID)
mqttc.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
mqttc.will_set(MQTT_STATUS_TOPIC, payload='disconnected', qos=0, retain=True)

mqttc.on_connect = on_connected
#mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

while True:
    logger.info(os.path.basename(__file__) + " - Attempting connection")
    # cast the port from 'unicode' to plain 'string'
    mqttc.connect(config["mqtt_host"], int(config["mqtt_port"]))
    mqttc.loop_start()
    client_loop = mqttc.loop(120)
    while client_loop == 0:
        try:
            publish_status(mqttc)
            time.sleep(60)   # sleep for 60 seconds before next call
            client_loop = mqttc.loop(.25) # blocks for 250ms
        except ValueError as err1:
            # we just don't publish bad readings
            logger.warning(os.path.basename(__file__) + " - [2] %s " % err.args)
            time.sleep(5)

    logger.info(os.path.basename(__file__) + " - exiting with %s" % str(client_loop))

#except Exception as err2:
#    logger.warning(os.path.basename(__file__) + " - [1] %s " % err.args)
