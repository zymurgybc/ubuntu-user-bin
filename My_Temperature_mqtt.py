#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os 
import sys

import json 
config_json = os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.json'
with open(config_json, 'r') as f:
    config = json.load(f)


import time 
import datetime 
import logging
import requests
# sudo pip install paho-mqtt
import paho.mqtt.client as mqtt
import socket
import traceback
import Queue
import smbus
import RPi.GPIO as GPIO

#import importlib.machinery   # python 3.3 & 3.4
#grovepi = SourceFileLoader("grovepi.py", "/usr/local/src/GrovePi/Software/Python/")
#BMP085  = SourceFileLoader("grove_i2c_barometic_sensor_BMP180.py","/usr/local/src/GrovePi/Software/Python/")

#import importlib.util   # python 3.5+
#spec1   = importlib.util.spec_from_file_location("grovepi.py", "/usr/local/src/GrovePi/Software/Python/")
#grovepi = importlib.util.module_from_spec(spec1)
#spec1.loader.exec_module(grovepi)
#
#spec2   = importlib.util.spec_from_file_location("grove_i2c_barometic_sensor_BMP180.py","/usr/local/src/GrovePi/Software/Python/")
#BMP180  = importlib.util.module_from_spec(spec2)
#spec2.loader.exec_module(BMP180)

sys.path.append("/usr/local/src/GrovePi/Software/Python/")
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
GROVE_DHT_SENSOR_PORT = 4
GROVE_DHT_SENSOR_TYPE = 0

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 600

MQTT_CLIENTID = socket.gethostname() + "_DHT11_pub"

MQTT_TOPIC_TEMP = "home/sensor/DHT11/" + socket.gethostname() + "/temperature"
MQTT_TOPIC_HUMI = "home/sensor/DHT11/" + socket.gethostname() + "/humidity"
MQTT_TOPIC_BARO = "home/sensor/DHT11/" + socket.gethostname() + "/barometer"
FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = config["mqtt_client_log"]


class MqttMessage:
    def __init__(self, topic, value):
        self.topic = topic
        self.value = value

message_queue = Queue.LifoQueue()

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
    if not message_queue.empty():
        aMessage = message_queue.get()
        mosq.publish(aMessage.topic, aMessage.value, qos = 1, retain = 1)
         

def on_subscribe(mosq, obj, mid, granted_qos):
    logger.info(os.path.basename(__file__) + " - subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    logger.info(os.path.basename(__file__) + " - Log: " + string)

def publish_dht11():
    try:
        [temp,humidity] = grovepi.dht(GROVE_DHT_SENSOR_PORT, GROVE_DHT_SENSOR_TYPE)
        #logger.info(os.path.basename(__file__) + " --- temp " + str(temp) + " - humi " + str(float(humidity) * 10))
        logger.info(os.path.basename(__file__) + " --- temp " + str(temp) + " - humi " + str(float(humidity)*10))

	# Skip to the next reading if a valid measurement couldn't be taken.
        #This might happen if the CPU is under a lot of load and the sensor
        # can't be reliably read (timing is critical to read the sensor).
        if humidity is None or temp is None:
            raise ValueError('Sensor reading failed')

        # occasional number are > 100 which is not viable
        #if humidity < 20: # and humidity > 0:
        #    message_queue.put(MqttMessage(MQTT_TOPIC_HUMI, float(humidity)*10.0))
        message_queue.put(MqttMessage(MQTT_TOPIC_HUMI, float(humidity)*10))

	message_queue.put(MqttMessage(MQTT_TOPIC_TEMP, float(temp)))

    except ValueError as err:
        # we just don't publish bad readings
        #print(err.args)
        logger.warning(os.path.basename(__file__) + " - publish_dht11: %s " % err.args)

def publish_barometer():
    try:
        pressure_long = bmp.readPressure()
        pressure_float = float(pressure_long)/1000
        message_queue.put(MqttMessage(MQTT_TOPIC_BARO, pressure_float))
        message_queue.put(MqttMessage(MQTT_TOPIC_BARO + "/units", "Kpa"))
    except Exception as err:
        # we just don't publish bad readings
        #print(err.args)
        logger.warning(os.path.basename(__file__) + " - publish_barometer: %s " % err.args)

def mqtt_publish():
    try:
        publish_barometer()
        publish_dht11()
    except Exception as err:
        # handle filed sends with a note in the log
        logger.warning(os.path.basename(__file__) + " - mqtt_publish call failed. {0} " % err.args)


logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('My_Temperature_mqtt')

client = mqtt.Client(MQTT_CLIENTID, clean_session=False)

# Use the JSON config to store the server reference
client.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
client.on_connect = on_connected
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_log = on_log

client.will_set( topic = "home/client/" + MQTT_CLIENTID, payload = "disconnected", qos=2, retain=1)

while True:
    try:
        logger.info(os.path.basename(__file__) + " - connecting" + " to mqtt://" + config["mqtt_host"] + ":" + config["mqtt_port"])

        # Use the JSON config to store the server reference
        client.connect(config["mqtt_host"], int(config["mqtt_port"]))
        client.loop_start()	

        _continue = 1
        while _continue:
            _continue = mqtt_publish()
            message_queue.put(MqttMessage("home/client/" + MQTT_CLIENTID, "connected"))
            # This will prime the loop
            if not message_queue.empty():
               aMessage = message_queue.get()
               client.publish(aMessage.topic, aMessage.value, qos = 1, retain = 1)
            # this waits while the current messages are sent
            time.sleep(30)
    except Exception as err:
        # handle filed sends with a note in the log
        logger.warning(os.path.basename(__file__) + " - mqtt loop failed.  Exception message: %s" % err.args)
        sys.exit(os.path.basename(__file__) + " - mqtt loop failed.  Exception message: %s" % err.args)
