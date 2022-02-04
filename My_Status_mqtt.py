#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os
import threading
from subprocess import check_output
import ctypes
import struct
import time
from datetime import datetime
import logging
import requests
import paho.mqtt.client as mqtt # sudo pip install paho-mqtt
import re
import sys
import socket
import traceback

import json

config_json = os.path.dirname(os.path.realpath(__file__)) + '/mqtt_config.json'
with open(config_json, 'r') as f:
    config = json.load(f)

MQTT_CLIENTID = socket.gethostname() + '_status_pub'
MQTT_STATUS_TOPIC = 'home/client/' + socket.gethostname() + '/status'
MQTT_UPDATE_TOPIC = 'home/client/' + socket.gethostname() + '/updated'

FORMAT = '%(asctime)-15s %(message)s'
LOG_FILENAME = config["mqtt_client_log"]
logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
logger = logging.getLogger('My_Status_mqtt')

def on_connected(mosq, userdata, flags, rc):
    host = mosq.updater.config["mqtt_host"]
    logger.info(os.path.basename(__file__) + " - " + host + " - mqtt connected")
    mosq.updater.publish_status()

#def on_message(mosq, obj, msg):
#    global message
#    host = mosq.updater.config["mqtt_host"]
#    print(host + " --> " + msg.topic + " + " + str(msg.qos) + " --> " + str(msg.payload))
#    message = msg.payload

def on_publish(mosq, obj, mid):
    host = mosq.updater.config["mqtt_host"]
    logger.info(os.path.basename(__file__) + " - " + host + " Published: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    host = mosq.updater.config["mqtt_host"]
    logger.info(os.path.basename(__file__) + " - " + host + " Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, message):
    host = mosq.updater.config["mqtt_host"]
    logger.info(os.path.basename(__file__) + " - " + host + " Log: " + message)

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

class mqtt_updater:

    def __init__(self, config):
        # print("Using ", type(config), " ", config)
        self.config = config
        self.mqttc = mqtt.Client(MQTT_CLIENTID)
        self.mqttc.username_pw_set(config["mqtt_client"], password=config["mqtt_password"])
        self.mqttc.will_set(MQTT_STATUS_TOPIC, payload='disconnected', qos=0, retain=True)
        self.mqttc.updater = self

        self.mqttc.on_connect = on_connected
        # self.mqttc.on_message = on_message
        self.mqttc.on_publish = on_publish
        self.mqttc.on_subscribe = on_subscribe
        self.mqttc.on_log = on_log

    def run(self):
        while True:
            logger.info(os.path.basename(__file__) + " - Attempting connection")
            # cast the port from 'unicode' to plain 'string'
            self.mqttc.connect(self.config["mqtt_host"], int(self.config["mqtt_port"]))
            self.mqttc.loop_start()
            self.client_loop = self.mqttc.loop(120)
            while self.client_loop == 0:
                try:
                    self.publish_status()
                    time.sleep(60)               # sleep for 60 seconds before next call
                    self.client_loop = self.mqttc.loop(.25) # blocks for 250ms
                except ValueError as err1:
                    # we just don't publish bad readings
                    logger.warning(os.path.basename(__file__) + " - run() %s " % err1.args)
                    time.sleep(5)

            logger.info(os.path.basename(__file__) + " - exiting with %s" % str(self.client_loop))

    def publish_status(self):
        my_status =  'connected ' + getIP()
        #print( my_status )
        self.mqttc.publish(MQTT_STATUS_TOPIC, my_status, qos = 1, retain = 1)
        logger.info(os.path.basename(__file__) + " - " + self.config["mqtt_host"] + " Sending status: " + my_status)
        my_updated = self.myUpdated()
        self.mqttc.publish(MQTT_UPDATE_TOPIC, my_updated, qos = 1, retain = 1)
        logger.info(os.path.basename(__file__) + " - " + self.config["mqtt_host"] + " Sending update: " + my_updated)

    def myUpdated(self):
        my_updated = '{{ "uname": {}, "DateTime": "{}", "Uptime": "{}" }}'.format(
            self.systemUname(),
            time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
            uptime())
        #print( my_updated )
        return my_updated

    def systemUname(self):
        uname = ' {{ "Empty": "true" }}'
        try:
            tupleString = str(os.uname()).replace("posix.uname_result(", '{ ').replace(")", ' }')
            #print(f'tuple {tupleString}')
            uname = re.sub("([a-zA-Z]*)=", "\"\\1\": ", tupleString)
            #print(f'uname {uname}')

        except Exception as err1:
             logger.warning(os.path.basename(__file__) + " - systemUname() %s " % err1.args)
             raise err1

        return uname




if __name__ == "__main__":
    for host in config["hosts"]:
        #print("Using " + host)
        updater = mqtt_updater(config["hosts"][host])
        t = threading.Thread(target=updater.run)
        t.start()
        t.join()

    #except Exception as err2:
    #    logger.warning(os.path.basename(__file__) + " - [1] %s " % err.args)

