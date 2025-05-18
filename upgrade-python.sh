#!/bin/bash
PYTHON_LOG="upgrade-python.$(date +'%Y-%m-%d').log"
PYTHON_ERR="upgrade-python.$(date +'%Y-%m-%d').err"

function upgrade_python_modules() {
  pyPath=$1
  pyVersion=$2
  pyFreeze="${pyPath}${pyVersion} -m pip freeze "

  eval "${pyFreeze} > ~/bin/tmp/${pyVersion}_$(date +"'%Y-%m-%d_%H%M'").freeze"
  eval "${pyFreeze} --local" \
      | grep -v '^\-e'             \
      | cut -d = -f 1              \
      | while IFS= read -r line
        do
           # Output the next command to the error and output logs to make tracking down problems simpler
           echo -e "\e[1m\e[46m\e[30msudo -H ${pyPath}${pyVersion} -m pip install --upgrade ${line}\e[0m\e[49m\e[39m" \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_LOG}" \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_ERR}"
           # Execute the command splitting errors into the shorter log
           sudo -H ${pyPath}${pyVersion} -m pip install --upgrade ${line}  \
                 2> >(tee -a "${HOME}/bin/tmp/${PYTHON_ERR}" > /dev/null ) \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_LOG}" 
        done
}

function enumerate_python_versions() {
#  verPython=("python2.7" "python3.4" "python3.5" "python3.5m" "python3.6" "python3.6m" "python3.7" "python3.8" "python3.9" )
  verPython=("python3.6" "python3.6m" "python3.7" "python3.8" "python3.9" "python3.10" "python3.11" "python3.12" "python3.13" )
  for py in "${verPython[@]}"
  do
    echo "Checking for ${py}..."
    if [ -f "/usr/bin/${py}" ]; then
      echo "    Found \"/usr/bin/${py}\" " \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_LOG}" \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_ERR}"
      sudo -H sh -c "/usr/bin/${py} -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi" \
                 2> >( tee -a "${HOME}/bin/tmp/${PYTHON_ERR}" >/dev/null ) \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_LOG}" 

      # http://ouimeaux.readthedocs.io/en/latest/installation.html
      # wemo wrapper in python :-)
      # python3 -m pip install ouimeaux

      # We'll upgrade all packages at the global level, but not for any virtual environments
      # http://stackoverflow.com/questions/2720014/upgrading-all-packages-with-pip
      echo "upgrade_python_modules \"/usr/bin/\" \"${py}\""
      upgrade_python_modules "/usr/bin/" "${py}"
    else
      echo "    \"/usr/bin/${py}\" does not appear to be available."
    fi

    # There may be more in a virtual environment, too
    target="`which ${py}`"
    if [ ! -z "${target}" ]; then
      location="$( cd "$( dirname "${target}" )" >/dev/null 2>&1 && pwd )"
      if [ $location != "/usr/bin" ];  then
        echo "    Found \"${target}\""
        sudo -H sh -c "${target} -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi"
        upgrade_python_modules ${location}/ ${py}
     fi
    else
      echo "    Did not find another ${py} location using the path."
    fi
  done

}

mkdir -p ~/bin/tmp
# delete old temporary files
find ~/bin/tmp/* -mtime +90 -exec rm {} \;
enumerate_python_versions
echo "  ========= Completed in $SECONDS" \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_LOG}" \
                 |  tee -a "${HOME}/bin/tmp/${PYTHON_ERR}"
