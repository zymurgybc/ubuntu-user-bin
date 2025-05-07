#!/usr/bin/env bash

#echo "Dummy message from ${HOSTNAME}." | mail --debug-level=9 --config-verbose -s "Simple Test Email" -- ${USER}
echo "Dummy message from ${HOSTNAME}.
$(ls -al `which sendmail`)" | mail -s "Simple Test Email" -- ${USER}
echo $?
