#!/bin/bash
HOME=/home/theather

# kill any running process and dump the help to /dev/null
sudo kill `ps -ef | grep mqtt-zway | grep -v mqtt-zway.sh | grep -v grep | awk '{print $2}'` 2>/dev/null

mqtt_client=`  jq .mqtt_client   < ${HOME}/bin/mqtt_config.json`
mqtt_password=`jq .mqtt_password < ${HOME}/bin/mqtt_config.json`
mqtt_host=`    jq .mqtt_host     < ${HOME}/bin/mqtt_config.json`
mqtt_port=`    jq .mqtt_port     < ${HOME}/bin/mqtt_config.json`
sudo /usr/local/bin/mqtt-zway \
    -c ${HOME}/bin/mqtt-zway.config  \
    -h mqtt://${mqtt_client}:${mqtt_password}@${mqtt_host}:${mqtt_port} \
    >> /var/log/mqtt-zway.log &
