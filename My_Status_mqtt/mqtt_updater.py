#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from tendo import singleton
#me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

import os
import threading
import time
from datetime import datetime
import logging
import requests
import paho.mqtt.client as mqtt # sudo pip install paho-mqtt
import re
import socket
import traceback

import json

if os.name == "posix":
    from My_Status_mqtt.Linux_Tools import Linux_Tools as tools
else:
    from My_Status_mqtt.Windows_Tools import Windows_Tools as tools

class mqtt_updater:

    def __init__(self, config, hostConfig, logger):
        '''
        Initialise instance/Constructor

        config is json object for the entire file
        hostConfig is the string name of the host to configure
        '''

        self.MQTT_CLIENTID = socket.gethostname() + '_status_pub'
        self.MQTT_STATUS_TOPIC = 'home/client/' + socket.gethostname() + '/status'
        self.MQTT_UPDATE_TOPIC = 'home/client/' + socket.gethostname() + '/updated'

        # print("Using ", type(config), " ", config)
        self.config = config
        self.hostConfig = hostConfig
        self.logger = logger
        self.tools = tools(logger)
        self.getClient()


    def getClient(self):
        hostConfig = self.config['hosts'][self.hostConfig]
        self.mqttc = mqtt.Client(self.MQTT_CLIENTID)
        self.mqttc.username_pw_set(hostConfig["mqtt_client"], password=hostConfig["mqtt_password"])
        self.mqttc.will_set(self.MQTT_STATUS_TOPIC, payload='disconnected', qos=0, retain=True)
        self.mqttc.updater = lambda : self.myUpdated()

        self.mqttc.on_connect = lambda mosq, userdata, flags, rc : self.on_connected(mosq, userdata, flags, rc)
        # self.mqttc.on_message = on_message
        self.mqttc.on_publish = lambda mosq, obj, mid : self.on_publish(mosq, obj, mid)
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_log = self.on_log

    def run(self):
        hostConfig = self.config['hosts'][self.hostConfig]
        while True:
            self.logger.info(os.path.basename(__file__) + " - Attempting connection")
            # cast the port from 'unicode' to plain 'string'
            self.mqttc.connect(hostConfig["mqtt_host"], int(hostConfig["mqtt_port"]))
            self.mqttc.loop_start()
            self.client_loop = self.mqttc.loop(120)
            while self.client_loop == 0:
                try:
                    self.publish_status()
                    time.sleep(60)               # sleep for 60 seconds before next call
                    self.client_loop = self.mqttc.loop(.25) # blocks for 250ms
                except ValueError as err1:
                    # we just don't publish bad readings
                    self.logger.warning(os.path.basename(__file__) + " - run() %s " % err1.args)
                    time.sleep(5)

            self.logger.info(os.path.basename(__file__) + " - exiting with %s" % str(self.client_loop))

    def publish_status(self):
        hostConfig = self.config['hosts'][self.hostConfig]
        my_status = {}
        my_status['Hostname'] = socket.gethostname()
        my_status['Status'] = 'connected'
        my_status['IP'] = self.tools.getIP()
        #print( my_status )
        self.mqttc.publish(self.MQTT_STATUS_TOPIC, json.dumps(my_status), qos = 1, retain = 1)
        self.logger.info(os.path.basename(__file__) + " - " + hostConfig["mqtt_host"] + " Sending status: " + my_status)
        my_updated = self.myUpdated()
        self.mqttc.publish(self.MQTT_UPDATE_TOPIC, my_updated, qos = 1, retain = 1)
        self.logger.info(os.path.basename(__file__) + " - " + hostConfig["mqtt_host"] + " Sending update: " + my_updated)

    def myUpdated(self):
        my_updated = '{{ "uname": {}, "DateTime": "{}", "Uptime": "{}" }}'.format(
            self.tools.systemUname(),
            time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
            self.tools.uptime())
        #print( my_updated )
        return my_updated

    def on_connected(self, mosq, userdata, flags, rc):
        self.logger.info(os.path.basename(__file__) + " - " + self.hostConfig + " - mqtt connected")
        self.publish_status()

    #def on_message(mosq, obj, msg):
    #    global message
    #    print(self.hostConfig + " --> " + msg.topic + " + " + str(msg.qos) + " --> " + str(msg.payload))
    #    message = msg.payload

    def on_publish(self, mosq, obj, mid):
        self.logger.info(os.path.basename(__file__) + " - " + self.hostConfig + " Published: " + str(mid))

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        self.logger.info(os.path.basename(__file__) + " - " + self.hostConfig + " Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mosq, obj, level, message):
        self.logger.info(os.path.basename(__file__) + " - " + self.hostConfig + " Log: " + message)

#def launchClient(config, host, logger):
#    #print("Using " + host)
#    t = threading.Thread(target=lambda task: updater = mqtt_updater(config, host, logger), updater.run())
#    t.start()
#    return t

