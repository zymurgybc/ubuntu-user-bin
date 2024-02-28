#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from tendo import singleton
#me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running
import os
import logging
import json
import threading
from My_Status_mqtt import mqtt_updater


def launchClient(config, host, logger):
    updater = mqtt_updater.mqtt_updater(config, host, logger)
    updater.run()

def launchClients():
    try:
        config_json = os.path.dirname(os.path.realpath(__file__)) + '/../mqtt_config.json'
        with open(config_json, 'r') as f:
            config = json.load(f)

        FORMAT = '%(asctime)-15s %(message)s'
        LOG_FILENAME = config["mqtt_client_log"]

        logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
        logger = logging.getLogger('My_Status_mqtt')

        threads = []
        for host in config["hosts"]:
            #threads.append(launchClient(config, host, logger))
            t = threading.Thread(target=launchClient, args=(config, host, logger))
            threads.append(t)

        for x in threads:
            x.start()

        for x in threads:
            x.join()

    except Exception as err:
        logger.warning(os.path.basename(__file__) + " - [1] %s " % err.args)


if __name__ == "__main__":
    launchClients()
