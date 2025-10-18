if [ $# -eq 0 ]; then
   echo "No user id supplied"
fi

if [ $# -eq 1 ]; then
   echo "No user password supplied"
fi

MQ_USER=$1
MQ_PWD=$2

sudo rabbitmqctl add_user ${MQ_USER} ${MQ_PWD}
sudo rabbitmqctl set_user_tags ${MQ_USER} IOT users MQTT
sudo rabbitmqctl set_permissions -p home ${MQ_USER} "^${MQ_USER}-.*" ".*" ".*"
#sudo rabbitmqctl set_permissions -p home ${MQ_USER} "(^${MQ_USER}|mqtt-subscription-${MQ_USER})-.*" ".*" ".*"
