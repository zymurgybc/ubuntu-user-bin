#!/bin/bash
mqtt_client=`  jq .mqtt_client   < ${HOME}/bin/mqtt_config.json`
mqtt_password=`jq .mqtt_password < ${HOME}/bin/mqtt_config.json`
mqtt_host=`    jq .mqtt_host     < ${HOME}/bin/mqtt_config.json`
mqtt_port=`    jq .mqtt_port     < ${HOME}/bin/mqtt_config.json`
sudo /usr/local/bin/mqtt-zway \
    -c ${HOME}/bin/mqtt-zway.config  \
    -h mqtt://${mqtt_client}:${mqtt_password}@${mqtt_host}:${mqtt_port}
