#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os
import sys
from subprocess import check_output
import time
import datetime
import logging
import requests
import paho.mqtt.client as mqtt # sudo pip install paho-mqtt
import socket
import traceback
import Queue

import json 
config_json = os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.json'
with open(config_json, 'r') as f:
    config = json.load(f)

FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = '/var/log/sinope_thermostat_mqtt.log'
logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('sinope_thermostat_mqtt')

MyConfig = {}
MyConfig["Nevi_UserId"] = "me"
MyConfig["mqtt_host"] = "192.168.1.50"
MyConfig["mqtt_port"] = 1883
MyConfig["mqtt_UserId"] = "TedsAsusLaptop"
MyConfig["mqtt_Password"] = "itsasecret"
MyConfig["mqtt_ClientId"] = socket.gethostname() + '_sinope_pub'

class MqttMessage:
    def __init__(self, topic, value):
        self.topic = topic
        self.value = value

message_queue = Queue.LifoQueue()

MQTT_TOPIC_TEMP = "home/sensor/temperature/" # + socket.gethostname()
MQTT_TOPIC_HUMI = "home/sensor/humidity/"    # + socket.gethostname()
MQTT_TOPIC_BARO = "home/sensor/barometer/"   # + socket.gethostname()
MQTT_STATUS = 'home/client/' + socket.gethostname() + '/sinope_pub'

def on_connected(client, userdata, rc):
     logger.info(os.path.basename(__file__) + " - mqtt connected")
     publish_status(client)

#def on_message(mosq, obj, msg):
#    global message
#    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
#    message = msg.payload

def on_publish(mosq, obj, mid):
    logger.info(os.path.basename(__file__) + " - Published: " + str(mid))
    if not message_queue.empty():
        aMessage = message_queue.get()
        mosq.publish(aMessage.topic, aMessage.value, qos = 1, retain = 1)

def on_subscribe(mosq, obj, mid, granted_qos):
    logger.info(os.path.basename(__file__) + " - Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    logger.info(os.path.basename(__file__) + " - Log: " + string)

def getIP():
    return check_output(["hostname", "--all-ip-addresses"])

def publish_status(client):
    my_status = 'connected ' + getIP()
    logger.info(os.path.basename(__file__) + " - Sending: " + my_status)
    publish_nevi_temp()
    client.publish(MQTT_STATUS, my_status, qos = 1, retain = 1)

def publish_nevi_temp():
    logger.info(os.path.basename(__file__) + " - Sending: " + MQTT_TOPIC_TEMP)
    message_queue.put(MqttMessage(MQTT_TOPIC_TEMP, float("19.5")))
    message_queue.put(MqttMessage(MQTT_TOPIC_TEMP + '/units', "C"))

mqttc = mqtt.Client(MyConfig["mqtt_ClientId"])
# Use the JSON config to store the credentials
mqttc.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
mqttc.will_set(MQTT_STATUS, payload='disconnected', qos=0, retain=True)

mqttc.on_connect = on_connected
#mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log

while True:
    logger.info(os.path.basename(__file__) + " - Attempting connection")
    # Use the JSON config to store the server reference
    print(config["mqtt_host"], int(config["mqtt_port"]))
    logger.info(os.path.basename(__file__) + " - Connectiing to %s:%s", config["mqtt_host"], config["mqtt_port"])
    mqttc.connect(config["mqtt_host"], int(config["mqtt_port"]))
    mqttc.loop_start()
    client_loop = mqttc.loop()
    while client_loop == 0:
        try:
            publish_status(mqttc)
            time.sleep(10)   # sleep for 30 seconds before next call
            client_loop = mqttc.loop()
        except ValueError as err1:
            # we just don't publish bad readings
            logger.warning(os.path.basename(__file__) + " - [2] %s " % err.args)
            time.sleep(5)

    logger.info(os.path.basename(__file__) + " - exiting with %s" % client_loop)

#except Exception as err2:
#    logger.warning(os.path.basename(__file__) + " - [1] %s " % err.args)
