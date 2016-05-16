#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os 
#from ConfigParser import SafeConfigParser
#config = SafeConfigParser()
#config.read(os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.ini')

config_json = os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.json'

import json 
with open(config_json, 'r') as f:
    config = json.load(f)

import sys 
import time 
import datetime 
import logging 
import requests
# sudo pip install paho-mqtt
import paho.mqtt.client as mqtt 
import socket 
import traceback

import smbus 
import RPi.GPIO as GPIO 
#sys.path.append("/home/pi/Source/GrovePi/Software/Python/")
from grovepi import grovepi 

from grove_i2c_barometic_sensor_BMP180 import BMP085

# Initialise the BMP180 and use STANDARD mode (default value)
# bmp = BMP085(0x77, debug=True)
bmp = BMP085(0x77, 1)

# To specify a different operating mode, uncomment one of the following:
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
# bmp = BMP085(0x77, 1)  # STANDARD Mode
# bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

# Example of sensor connected to Raspberry Pi pin 23
GROVE_DHT11_SENSOR = 2

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 600

def on_connected(client, userdata, rc):
	#status_will = {"topic": "client/" + MQTT_CLIENTID, "payload": "offline", "qos":1, "retain":1}
	#client.publish("client/" + MQTT_CLIENTID, "connected", qos = 1, retain = 1, will = status_will)
	logger.info(os.path.basename(__file__) + " - mqtt connected %s" % client)

def on_message(mosq, obj, msg):
	global message
	logger.info(os.path.basename(__file__) + " - message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	message = msg.payload

def on_publish(mosq, obj, mid):
	logger.info(os.path.basename(__file__) + " - published mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
	logger.info(os.path.basename(__file__) + " - subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
	logger.info(os.path.basename(__file__) + " - Log: " + string)

def publish_dht11(tempCli, humiCli):
	try:
		[temp,humidity] = grovepi.dht(GROVE_DHT11_SENSOR,0)
	        # Skip to the next reading if a valid measurement couldn't be taken.
        	# This might happen if the CPU is under a lot of load and the sensor
	        # can't be reliably read (timing is critical to read the sensor).
        	if humidity is None or temp is None:
                	raise ValueError('Sensor reading failed')

	        tempCli.publish(MQTT_TOPIC_TEMP, temp, qos = 1, retain = 1)
        	humiCli.publish(MQTT_TOPIC_HUMI, humidity, qos = 1, retain = 1)

	except ValueError as err:
		# we just don't publish bad readings
		#print(err.args)
		logger.warning(os.path.basename(__file__) + " - %s " % err.args)

def publish_barometer(baroCli):
        try:
		#bmp.update()
		pressure_long = bmp.readPressure()
		pressure_float = float(pressure_long)/100
		#logger.info(os.path.basename(__file__) + " - %s " % type(pressure_float))
        	baroCli.publish(MQTT_TOPIC_BARO, pressure_float, qos = 1, retain = 1)
		#logger.info(os.path.basename(__file__) + " - %s " % bmp)
	except Exception as err:
		# we just don't publish bad readings
		#print(err.args)
		logger.warning(os.path.basename(__file__) + " - %s " % err.args)


MQTT_STATUS_CLIENTID = socket.gethostname() + '_CONN_pub'
MQTT_TEMP_CLIENTID   = socket.gethostname() + '_TEMP_pub'
MQTT_HUMI_CLIENTID   = socket.gethostname() + '_HUMI_pub'
MQTT_BARO_CLIENTID   = socket.gethostname() + '_BARO_pub'

MQTT_TOPIC_TEMP = 'home/sensor/temperature/' + socket.gethostname()
MQTT_TOPIC_HUMI = 'home/sensor/humidity/'    + socket.gethostname()
MQTT_TOPIC_BARO = 'home/sensor/barometer/'   + socket.gethostname()
FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = '/var/log/mqtt_client.log'

logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('My_Temperature_mqtt')

client_status = mqtt.Client(MQTT_STATUS_CLIENTID)
client_status.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
#client_status.on_connect = on_connected
#client_status.on_message = on_message
#client_status.on_publish = on_publish
#client_status.on_subscribe = on_subscribe
client_status.on_log = on_log

client_temp = mqtt.Client(MQTT_TEMP_CLIENTID)
client_temp.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
client_temp.on_log = on_log

client_humi = mqtt.Client(MQTT_HUMI_CLIENTID)
client_humi.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
client_humi.on_log = on_log

client_baro = mqtt.Client(MQTT_BARO_CLIENTID)
client_baro.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
client_baro.on_log = on_log

client_status.connect('wasabi', 1883)
client_temp.connect('wasabi', 1883)
client_humi.connect('wasabi', 1883)
client_baro.connect('wasabi', 1883)

client_status.loop_start()	
client_status.publish( topic = "client/" + MQTT_STATUS_CLIENTID, payload = "connected", qos = 1, retain = 1)
client_status.will_set(topic = "client/" + MQTT_STATUS_CLIENTID, payload = "offline", qos = 1, retain = 1)

_continue = 1
while _continue:
	publish_dht11(client_temp, client_humi)
	publish_barometer(client_baro)

	time.sleep(5)
	status_loop = client_status.loop()
	temp_loop = client_temp.loop()
	humi_loop = client_humi.loop()
	baro_loop = client_baro.loop()
	logger.info(os.path.basename(__file__) + " - status %i, temp %i, humi %i, baro %i", status_loop, temp_loop, humi_loop, baro_loop)

	_continue = (status_loop == 0) and (temp_loop == 0) and (humi_loop == 0)  and (baro_loop == 0)
