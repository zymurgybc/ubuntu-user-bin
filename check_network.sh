#!/bin/bash
# http://www.linuxquestions.org/questions/linux-networking-3/script-to-check-connection-and-restart-network-if-down-262281/
ROUTER_IP=192.168.1.1
TEST_LOG=/var/log/check_network.log

echo ====================                >> $TEST_LOG
echo `date +"%Y-%m-%d %T"`               >> $TEST_LOG
echo ping result = `ping -c1 $ROUTER_IP` >> $TEST_LOG
echo --------------------                >> $TEST_LOG
lsusb                                    >> $TEST_LOG

( ! ping -c1 $ROUTER_IP >/dev/null 2>&1 ) && service networking restart >/dev/null 2>&1

sleep 15

if [ -z "`ping -c1 $ROUTER_IP >/dev/null 2>&1`" ]; then
    logger Network Restart Type 2
    service networking restart >/dev/null 2>&1
fi
