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
import uuid;
import json

if os.name == "posix":
    from My_Status_mqtt.Linux_Tools import Linux_Tools as tools
    #import Linux_Tools as tools
else:
    from My_Status_mqtt.Windows_Tools import Windows_Tools as tools

class mqtt_updater:

    def __init__(self, config, hostConfig, logger):
        '''
        Initialise instance/Constructor

        config is json object for the entire file
        hostConfig is the string name of the host to configure
        '''
        try:
            self.MQTT_CLIENTID = socket.gethostname() + '_status_pub'
            self.MQTT_STATUS_TOPIC = 'home/client/' + socket.gethostname() + '/status'
            self.MQTT_UPDATE_TOPIC = 'home/client/' + socket.gethostname() + '/updated'
            self.MQTT_SENDMAIL_TOPIC = 'home/client/' + socket.gethostname() + '/sendmail'

            # print("Using ", type(config), " ", config)
            self.config = config
            self.hostConfig = hostConfig
            self.logger = logger
            self.tools = tools(logger)
            self.getClient()
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "10", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)


    def getClient(self):
        '''
        Each updater object creates its own mqtt client
        '''
        try:
            hostConfig = self.config['hosts'][self.hostConfig]
            self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.MQTT_CLIENTID)
            self.mqttc.username_pw_set(hostConfig["mqtt_client"], password=hostConfig["mqtt_password"])
            testament ={}
            testament["messageId"] = str(uuid.uuid4())
            testament['Hostname'] = socket.gethostname()
            testament['Status']='disconnected'
            testament['IP']=self.tools.getIP()
            self.mqttc.will_set(self.MQTT_STATUS_TOPIC, payload=json.dumps(testament), qos=0, retain=True)
            self.mqttc.updater = lambda : self.myUpdated()

            self.mqttc.on_connect = lambda mosq, userdata, flags, rc : self.on_connected(mosq, userdata, flags, rc)
            # self.mqttc.on_message = on_message
            self.mqttc.on_publish = lambda mosq, obj, mid : self.on_publish(mosq, obj, mid)
            self.mqttc.on_subscribe = self.on_subscribe
            self.mqttc.on_log = self.on_log
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "20", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def run(self):
        try:
            hostConfig = self.config['hosts'][self.hostConfig]
            while True:
                log_message = os.path.basename(__file__) + " - Attempting connection to " + hostConfig["mqtt_host"]
                if(self.logger is not None):
                    self.logger.info(log_message)
                else:
                    print("Info: ", log_message)

                # cast the port from 'unicode' to plain 'string'
                self.mqttc.connect(hostConfig["mqtt_host"], int(hostConfig["mqtt_port"]))
                self.mqttc.loop_start()
                self.client_loop = self.mqttc.loop(120)
                while self.client_loop == 0:
                    try:
                        self.publish_status()
                        self.publish_sendmail()
                        time.sleep(60)               # sleep for 60 seconds before next call
                        self.client_loop = self.mqttc.loop(.25) # blocks for 250ms
                    except ValueError as err1:
                        err_str = '{}'.format(*err.args)
                        log_message = '%s - [%s] %s' % (os.path.basename(__file__), "31", err_str)
                        # we just don't publish bad readings
                        if(self.logger is not None):
                            self.logger.warning(log_message)
                        else:
                            print("Warn: ", log_message)
                        time.sleep(5)

                log_message = '%s - [%s] %s ==> %s' % os.path.basename(__file__), "39", hostConfig["mqtt_host"], " - exiting with %s" % str(self.client_loop)
                if(self.logger is not None):
                    self.logger.info(log_message)
                else:
                    print("Info: ", log_message)
        except Exception as err:
            err_str = '{}'.format(type(err), err)
            log_message = '%s - [%s] %s => %s' % (os.path.basename(__file__), "30", hostConfig["mqtt_host"], err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def publish_status(self):
        try:
            hostConfig = self.config['hosts'][self.hostConfig]
            my_status = {}
            my_status["messageId"] = str(uuid.uuid4())
            my_status['Hostname'] = socket.gethostname()
            my_status['Status'] = 'connected'
            my_status['IP'] = self.tools.getIP()
            #print( my_status )
            self.mqttc.publish(self.MQTT_STATUS_TOPIC, json.dumps(my_status), qos = 1, retain = 1)
            log_message = os.path.basename(__file__) + " - " + hostConfig["mqtt_host"] + " Sending status: " + str(my_status)
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
            my_updated = self.myUpdated()
            self.mqttc.publish(self.MQTT_UPDATE_TOPIC, my_updated, qos = 1, retain = 1)
            log_message = os.path.basename(__file__) + " - " + hostConfig["mqtt_host"] + " Sending update: " + my_updated
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "40", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def publish_sendmail(self):
        try:
            hostConfig = self.config['hosts'][self.hostConfig]
            my_status = {}
            my_status["messageId"] = str(uuid.uuid4())
            my_status['Hostname'] = socket.gethostname()
            my_status['sendmail'] = 'not checked'
            my_status['IP'] = self.tools.getIP()
            #print( my_status )
            self.mqttc.publish(self.MQTT_SENDMAIL_TOPIC, json.dumps(my_status), qos = 1, retain = 1)
            log_message = os.path.basename(__file__) + " - " + hostConfig["mqtt_host"] + " Sending sendmail info: " + str(my_status)
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
            my_updated = self.myUpdated()
            self.mqttc.publish(self.MQTT_UPDATE_TOPIC, my_updated, qos = 1, retain = 1)
            log_message = os.path.basename(__file__) + " - " + hostConfig["mqtt_host"] + " Sending sendmail info: " + my_updated
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
        except Exception as err:
            err_str = '{}'.format(type(err), *err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "40", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def myUpdated(self):
        try:
            my_updated = '{{ "uname": {}, "DateTime": "{}", "Uptime": "{}" }}'.format(
                self.tools.systemUname(),
                time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
                self.tools.uptime())
            #print( my_updated )
            return my_updated
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "50", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def on_connected(self, mosq, userdata, flags, rc):
        try:
            log_message = os.path.basename(__file__) + " - " + self.hostConfig + " - mqtt connected"
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
            self.publish_status()
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "60", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    #def on_message(mosq, obj, msg):
    #    try:
    #        global message
    #        print(self.hostConfig + " --> " + msg.topic + " + " + str(msg.qos) + " --> " + str(msg.payload))
    #        message = msg.payload
    #    except Exception as err:
    #        log_message = os.path.basename(__file__) + " - [1] %s " % err.args
    #        if(self.logger is not None):
    #            self.logger.warning(log_message)
    #        else:
    #            print(log_message)

    def on_publish(self, mosq, obj, mid):
        try:
            log_message = os.path.basename(__file__) + " - " + self.hostConfig + " Published: " + str(mid)
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "70", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        try:
            log_message = os.path.basename(__file__) + " - " + self.hostConfig + " Subscribed: " + str(mid) + " " + str(granted_qos)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print("Info: ", log_message)
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "80", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

    def on_log(self, mosq, obj, level, message):
        try:
            log_message = os.path.basename(__file__) + " - " + self.hostConfig + " Log: " + message
            if(self.logger is not None):
                self.logger.info(log_message)
            else:
                print("Info: ", log_message)
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "90", err_str)
            if(self.logger is not None):
                self.logger.warning(log_message)
            else:
                print(log_message)

