#!/bin/bash
RABBIT_STATE=`/etc/init.d/rabbitmq-server status | grep Active: | cut -d ' ' -f 5`
if [ "$RABBIT_STATE" = "active" ]; then
    echo "Found active process; trying to restart"
    /etc/init.d/rabbitmq-server try-restart
else
    echo "RabbitMQ is ${RABBIT_STATE}; trying to start"
    /etc/init.d/rabbitmq-server start
fi

pkill -f mqspeak
#if [ ! -f "${HOME}/bin/mqspeak.out" ]; then
    touch ${HOME}/bin/mqspeak.out
    chown theather.theather ${HOME}/bin/mqspeak.out
    chmod 666 ${HOME}/bin/mqspeak.out
#fi
nohup /usr/bin/python3 /usr/local/bin/mqspeak 2>&1 >> ${HOME}/bin/mqspeak.out &
