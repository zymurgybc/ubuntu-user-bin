#!/bin/bash

if [ -z $1 ]; then
  echo "You must enter a parameter:"
  echo "\"on\"  - turn the lights on to white"
  echo "\"off\" - turn the lights off"
  echo "\evening\" - turn lights on \(5\) in green"
  exit -1
fi

ZWAY_USER=admin
ZWAY_PASSWD=not2bright
ZWAY_ACTION=99
LED_ACTION1="c 1 b 9"
LED_ACTION2="c 1 c white"
CMD_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
command=$1

   case $command in
   "off"|"OFF")
      echo "Found off parameter"
      LED_ACTION1="c 1 b 0"
      LED_ACTION2="c 1 c white"
      ZWAY_ACTION=0;;
   "evening"|"EVENING")
      echo "Found evening parameter"
      LED_ACTION1="c 1 b 9"
      LED_ACTION2="c 1 c green"
      ZWAY_ACTION=40;;
   *)
      echo "Using on parameter"
      #LED_ACTION1=c 1 b 9
      #LED_ACTION2=c 1 c white
      #ZWAY_ACTION=99
   esac


   wget --auth-no-challenge --user ${ZWAY_USER} --password ${ZWAY_PASSWD} -P ~/tmp/ \
        http://razberry:8083/ZWaveAPI/Run/devices[16].instances[0].Basic.Set\(${ZWAY_ACTION}\) 2>/dev/null

   sleep 5
   #echo "${CMD_DIR}/led.sh ${LED_ACTION1}"
   ${CMD_DIR}/led.sh ${LED_ACTION1}
   sleep 1
   #echo "${CMD_DIR}/led.sh ${LED_ACTION2}"
   ${CMD_DIR}/led.sh ${LED_ACTION2}


