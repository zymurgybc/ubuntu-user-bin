#!/bin/bash
#http://stackoverflow.com/questions/16828035/linux-command-to-check-if-a-shell-script-is-running-or-not
result=`sudo ps aux | grep -i "[Cc]lock27\.py" | grep -v "grep" | wc -l`
if [ $result -lt 1 ]; then
    echo "script is not running"
    #sudo /etc/init.d/clock.py &
#else
#    echo "script is running"
fi
