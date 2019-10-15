#!/bin/bash

verPython=("python2.7" "python3.4" "python3.5" "python3.5m" "python3.6" "python3.6m" "python3.7" )
for i in "${verPython[@]}"
do
    echo "Checking for ${i}..."
    if [ -f "/usr/bin/${i}" ]; then
        echo "    Found \"/usr/bin/${i}\" "
        sudo -H sh -c "/usr/bin/${i} -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi"

        /usr/bin/${i} -m pip freeze > "~/bin/tmp/${i}_requirements_$(date +"'%Y%m%d_%H%M'")"
       # We'll upgrade all packages at the global level, but not for any virtual environments
       # http://stackoverflow.com/questions/2720014/upgrading-all-packages-with-pip
       /usr/bin/${i} -m pip freeze --local \
               | grep -v '^\-e'             \
               | cut -d = -f 1              \
               | xargs -t -n1 sudo -H /usr/bin/${i} -m pip install --upgrade
    else
        echo "    \"/usr/bin/${i}\" does not appear to be available."
    fi

    # There may be more in a virtual environment, too
    if [ ! -z "`which ${i}`" ]; then
        echo "    Found \"`which ${i}`\""
        sudo -H sh -c "`which ${i}` -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi"

# http://ouimeaux.readthedocs.io/en/latest/installation.html
# wemo wrapper in python :-)
# python3 -m pip install ouimeaux
    else
        echo "    ${i} does not appear to be available."
    fi
done

