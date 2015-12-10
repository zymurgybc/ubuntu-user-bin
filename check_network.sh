#!/bin/bash
# http://www.linuxquestions.org/questions/linux-networking-3/script-to-check-connection-and-restart-network-if-down-262281/
ROUTER_IP=192.168.1.1
( ! ping -c1 $ROUTER_IP >/dev/null 2>&1 ) && service network restart >/dev/null 2>&1
