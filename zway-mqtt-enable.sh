#!/bin/bash
# http://wetwa.re/?p=136
# http://blog.hekkers.net/tag/z-way-javascript-api/
# http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO-8.html
ZWAY=/opt/z-way-server/automation

function append {
grep -q -F $1 $2 ||  echo $1 >> $2
}

append python                          "${ZWAY}/.syscommands"
append "executeFile(\"zway-mqtt.js\")" "${ZWAY}/main.js"

if [ ! -f "${ZWAY}/zway-mqtt.js" ]; then
    ln /home/pi/bin/zway-mqtt.js       "${ZWAY}/zway-mqtt.js"
fi
if [ ! -f "${ZWAY}/mqtt_config.json" ]; then
    ln /home/pi/bin/mqtt_config.json   "${ZWAY}/mqtt_config.json"
fi
