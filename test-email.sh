echo "Dummy message from ${HOSTNAME}." | mail --debug-level=9 --config-verbose -s "Simple Test Email" zymurgy.bc@gmail.com
echo $?
