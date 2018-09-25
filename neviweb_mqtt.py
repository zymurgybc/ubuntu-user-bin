#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Adapted from https://gist.github.com/mdrovdahl/0af14b84da43fb1801fe212ffc5ff30c

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import sys
import os
import requests
import json
import socket
import logging
import time
# sudo pip install paho-mqtt
import paho.mqtt.client as mqtt

is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as Queue
else:
    import queue as Queue

config_neviweb = os.path.dirname(os.path.realpath(__file__)) + '/neviweb.json'
with open(config_neviweb, 'r') as f:
    nevi_config = json.load(f)

config_mqtt = os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.json'
with open(config_mqtt, 'r') as f:
    mqtt_config = json.load(f)

MQTT_CLIENTID = socket.gethostname() + "_NeviWeb_pub"
MQTT_TOPIC_TEMP     = "home/sensor/thermostat/%s/temperature"
MQTT_TOPIC_SETPOINT = "home/sensor/thermostat/%s/setpoint"
FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = mqtt_config["mqtt_client_log"]

def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))

class MqttMessage:
    def __init__(self, topic, value):
        self.topic = topic
        self.value = value

def on_connected(client, userdata, rc):
    logger.info(os.path.basename(__file__) + " - mqtt connected %s" % client)

def on_message(mosq, obj, msg):
    global message
    logger.info(os.path.basename(__file__) + " - message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    message = msg.payload

def on_publish(mosq, obj, mid):
    logger.info(os.path.basename(__file__) + " - published mid: " + str(mid))
    if not message_queue.empty():
        aMessage = message_queue.get()
        mosq.publish(aMessage.topic, aMessage.value, qos = 1, retain = 1)

def on_subscribe(mosq, obj, mid, granted_qos):
    logger.info(os.path.basename(__file__) + " - subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    logger.info(os.path.basename(__file__) + " - Log: " + string)

def mosquittoClient():
	client = mqtt.Client(MQTT_CLIENTID, clean_session=False)
	# Use the JSON config to store the server reference
	client.username_pw_set(mqtt_config["mqtt_client"], password=mqtt_config["mqtt_password"])
	client.on_connect = on_connected
	client.on_message = on_message
	client.on_publish = on_publish
	client.on_subscribe = on_subscribe
	client.on_log = on_log
	client.will_set( topic = "home/client/" + MQTT_CLIENTID, payload = "disconnected", qos=2, retain=1)
	logger.info(os.path.basename(__file__) + " - connecting" + " to mqtt://" + mqtt_config["mqtt_host"] + ":" + mqtt_config["mqtt_port"])
	return client

def mosquittoPublish():
	try:
		neviSession = neviwebLogin()
		neviGateways = neviwebGateways(neviSession["session"])
		for gateway in neviGateways:
			devices = neviwebDevices(neviSession["session"], gateway["id"])
			for device in devices:
				deviceData = neviwebData(neviSession["session"], device["id"])
				message_queue.put(MqttMessage(MQTT_TOPIC_TEMP % device["name"], deviceData["temperature"]))
				message_queue.put(MqttMessage(MQTT_TOPIC_SETPOINT % device["name"], deviceData["setpoint"]))
	except Exception as err:
		# handle filed sends with a note in the log
		logger.warning(os.path.basename(__file__) + " - mqtt_publish call failed. {0} " % err.args)

def neviwebLogin():
	uri = nevi_config["server"]
	path = 'api/login'
	payload = {'email': nevi_config["email"], 'password': nevi_config["password"], 'stayConnected': '0'}

	r = requests.post(uri+path, data=payload) 
	return r.json()

# TODO To check that a request is successful, use r.raise_for_status()
# or check r.status_code is what you expect.
def neviwebGateways(sessionid):
	uri = nevi_config["server"]
	path = 'api/gateway'
	headers = {'Session-Id': sessionid}
	r = requests.get(uri+path, headers=headers)
	gatewayList = r.json()
	return gatewayList

# TODO if no gatetway, throw an error and logout
def neviwebDevices(sessionid, gatewayid):
	uri = nevi_config["server"]
	path = 'api/device'
	headers = {'Session-Id': sessionid}
	payload = {'gatewayId': gatewayid}
	r = requests.get(uri+path, headers=headers, params=payload)
	devices = r.json()
	return devices

def neviwebData(sessionid, deviceid):
	uri = nevi_config["server"]
	path = 'api/device/'+str(deviceid)+'/data?force=1'
	headers = {'Session-Id': sessionid}
	r = requests.get(uri+path, headers=headers)
	deviceData = r.json()
	return deviceData

# TODO make this a generic formatTemp(temp,format) function
def cToF(temp):
    return (str((9.0/5.0*float(temp)+32)))

logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('neviweb_mqtt')
message_queue = Queue.LifoQueue()

client = mosquittoClient()

while True:
	try:
		# Use the JSON config to store the server reference
		client.connect(mqtt_config["mqtt_host"], int(mqtt_config["mqtt_port"]))
		client.loop_start()
		_continue = 1

		while _continue:
			_continue = mosquittoPublish()  # fill the queue
                        statusmsg = "home/client/" + MQTT_CLIENTID, "connected"
			message_queue.put(MqttMessage(statusmsq))
			# This will prime the loop
			while not message_queue.empty():
				aMessage = message_queue.get()
				client.publish(aMessage.topic, aMessage.value, qos = 1, retain = 1)
				# this waits while the current messages are sent
			time.sleep(30)
	except Exception as err:
		# handle filed sends with a note in the log
		logger.warning(os.path.basename(__file__) + " - mqtt loop failed.  Exception message: %s" % err.args)
		sys.exit(os.path.basename(__file__) + " - mqtt loop failed.  Exception message: %s" % err.args)
                dump(err)
                # could be a session problem, so log back into neviweb
		neviSession = neviwebLogin()
