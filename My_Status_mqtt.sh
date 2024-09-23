
USER_HOME=/home/theather
VENV=${USER_HOME}/.local/python3

if [ -x "${VENV}/bin/python3.12" ]; then
   PYTHON_EXEC="${VENV}/bin/python3.12"
elif [ -x "${VENV}/bin/python3.11" ]; then
   PYTHON_EXEC="${VENV}/bin/python3.11"
fi

cd ${USER_HOME}/bin
#PATH=${VENV}/bin/:${USER_HOME}/bin/:${PATH}   # Handled by activate script?
PYTHON_PATH=${VENV}/bin:${USER_HOME}/bin:${PYTHON_PATH}

. ${VENV}/bin/activate
${PYTHON_EXEC} -m My_Status_mqtt 2>&1 | /usr/bin/ts '[%Y-%m-%d %H:%M:%S]' >> /var/log/mqtt_client.log
