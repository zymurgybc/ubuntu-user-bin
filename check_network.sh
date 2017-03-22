#!/bin/bash
# http://www.linuxquestions.org/questions/linux-networking-3/script-to-check-connection-and-restart-network-if-down-262281/
ROUTER_IP=192.168.1.1
TEST_LOG=/var/log/check_network.log
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ====================                >> $TEST_LOG
echo `date +"%Y-%m-%d %T"`               >> $TEST_LOG
echo ping result = `ping -c1 $ROUTER_IP` >> $TEST_LOG
echo --------------------                >> $TEST_LOG
lsusb                                    >> $TEST_LOG

#( ! ping -c1 $ROUTER_IP >/dev/null 2>&1 ) && service networking restart >/dev/null 2>&1
#
#sleep 15
#
#SECOND=`ping -c1 $ROUTER_IP >/dev/null 2>&1`
#if [ -z "${SECOND}" ]; then
#    logger Network Restart Type 2.1
#    echo logger Network Restart Type 2.1 >> $TEST_LOG
#    echo Second ping: \<${SECOND}\>    >> $TEST_LOG
#    echo -------------------- RESTART  >> $TEST_LOG
#    service networking restart 2>&1    >> $TEST_LOG
#fi



# http://weworkweplay.com/play/rebooting-the-raspberry-pi-when-it-loses-wireless-connection-wifi/
ping -c4 $ROUTER_IP 2>&1 > /dev/null

if [ $? != 0 ]; then
  echo -------------------- RESTART               >> $TEST_LOG
  #sudo /sbin/shutdown -r now
  #/usr/sbin/service networking restart 2>&1      >> $TEST_LOG
  /bin/systemctl daemon-reload && /bin/systemctl restart networking  2>&1         >> $TEST_LOG
  echo `date +"%Y-%m-%d %T"`                      >> $TEST_LOG
  echo second ping result = `ping -c1 $ROUTER_IP` >> $TEST_LOG
  ${DIR}/myip.up
fi
