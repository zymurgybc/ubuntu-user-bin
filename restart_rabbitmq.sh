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
nohup mqspeak &
