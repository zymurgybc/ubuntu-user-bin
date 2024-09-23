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
    try:
        updater = mqtt_updater.mqtt_updater(config, host, logger)
        updater.run()
    except Exception as err:
        err_str = '{}'.format(*err.args)
        log_message = '%s - [%s] %s' % (os.path.basename(__file__), "300", err_str)
        if(logger is not None):
            logger.warning(log_message)
        else:
            print(log_message)

def launchClients():
    logger = None
    try:
        config_json = os.path.dirname(os.path.realpath(__file__)) + '/../mqtt_config.json'
        with open(config_json, 'r') as f:
            config = json.load(f)

        FORMAT = '%(asctime)-15s %(message)s'
        LOG_FILENAME = config["mqtt_client_log"]

        try:
            # Debugging as a normal user will probably throw "Permission denied" on the log
            logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,level=logging.DEBUG)
            logger = logging.getLogger('My_Status_mqtt')
        except Exception as err:
            err_str = '{}'.format(*err.args)
            log_message = '%s - [%s] %s' % (os.path.basename(__file__), "100", err_str)
            if(logger is not None):
                logger.warning(log_message)
            else:
                print(log_message)

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
        err_str = '{}'.format(*err.args)
        log_message = '%s - [%s] %s' % (os.path.basename(__file__), "200", err_str)
        if(logger is not None):
            logger.warning(log_message)
        else:
            print(log_message)

if __name__ == "__main__":
    launchClients()
