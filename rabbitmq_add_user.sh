if [ $# -lt 1 ]; then
   echo "Usage: $0 <user> <password>"
   echo "No user id supplied"
   exit 1
fi

if [ $# -lt 2 ]; then
   echo "Usage: $0 <user> <password>"
   echo "No user password supplied"
   exit 1
fi

MQ_USER=$1
MQ_PWD=$2

sudo rabbitmqctl add_user "${MQ_USER}" "${MQ_PWD}"
sudo rabbitmqctl set_user_tags "${MQ_USER}" IOT users MQTT
# Grant access to both '/' and 'home' vhosts (consistent with Ansible fix-user-vhosts)
sudo rabbitmqctl set_permissions -p / "${MQ_USER}" ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p home "${MQ_USER}" "^${MQ_USER}-.*" ".*" ".*"
#sudo rabbitmqctl set_permissions -p home "${MQ_USER}" "(^${MQ_USER}|mqtt-subscription-${MQ_USER})-.*" ".*" ".*"
