
USER_HOME=/home/theather
VENV=${USER_HOME}/.local/python3

cd ${USER_HOME}/bin
PATH=${VENV}/bin/:${USER_HOME}/bin/:%PATH%
PYTHON_PATH=${VENV}/bin:${USER_HOME}/bin:${PYTHON_PATH}

#${USER_HOME}/.local/python3/bin/python3.11 -m My_Status_mqtt 2>&1 | /usr/bin/ts '[\%Y-\%m-\%d \%H:\%M:\%S]' >> /var/log/mqtt_client.log
source ${VENV}/bin/activate
${VENV}/bin/python3.11 -m My_Status_mqtt 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> /var/log/mqtt_client.log
