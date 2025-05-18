
USER_HOME=/home/theather
VENV=${USER_HOME}/.local/python3
MQTT_LOG=/var/log/mqtt_client.log

if [ -x "${VENV}/bin/python3.13" ]; then
   PYTHON_EXEC="${VENV}/bin/python3.13"
elif [ -x "${VENV}/bin/python3.12" ]; then
   PYTHON_EXEC="${VENV}/bin/python3.12"
elif [ -x "${VENV}/bin/python3.11" ]; then
   PYTHON_EXEC="${VENV}/bin/python3.11"
fi

cd ${USER_HOME}/bin
#PATH=${VENV}/bin/:${USER_HOME}/bin/:${PATH}   # Handled by activate script?
PYTHON_PATH=${VENV}/bin:${USER_HOME}/bin:${PYTHON_PATH}

echo MQTT_LOG="${MQTT_LOG}"       | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ${MQTT_LOG}
echo USER_HOME="${USER_HOME}"     | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ${MQTT_LOG}
echo VENV="${VENV}"               | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ${MQTT_LOG}
echo PYTHON_EXEC="${PYTHON_EXEC}" | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ${MQTT_LOG}

. ${VENV}/bin/activate
${PYTHON_EXEC} -m My_Status_mqtt 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> ${MQTT_LOG}
