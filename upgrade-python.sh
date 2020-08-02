#!/bin/bash
PYTHON_FRZ="upgrade-python.$(date +'%Y-%m-%d').freeze"
PYTHON_LOG="upgrade-python.$(date +'%Y-%m-%d').log"
PYTHON_ERR="upgrade-python.$(date +'%Y-%m-%d').err"

function upgrade_python_modules() {
  pyPath=$1
  pyVersion=$2
  pyFreeze="${pyPath}${pyVersion} -m pip freeze "

  eval "${pyFreeze} > ~/bin/tmp/${pyVersion}_requirements_$(date +"'%Y%m%d_%H%M'")"
  # We'll upgrade all packages at the global level, but not for any virtual environments
  # http://stackoverflow.com/questions/2720014/upgrading-all-packages-with-pip
  eval "${pyFreeze} --local" \
      | grep -v '^\-e'             \
      | cut -d = -f 1              \
      | while IFS= read -r line
        do
           echo -e "\e[1m\e[46m\e[30msudo -H ${pyPath}${pyVersion} -m pip install --upgrade ${line}\e[0m\e[49m\e[39m"
           sudo -H ${pyPath}${pyVersion} -m pip install --upgrade ${line}
        done
}

function enumerate_python_versions() {
  verPython=("python2.7" "python3.4" "python3.5" "python3.5m" "python3.6" "python3.6m" "python3.7" "python3.8" )
  for py in "${verPython[@]}"
  do
    echo "Checking for ${py}..."
    if [ -f "/usr/bin/${py}" ]; then
      echo "    Found \"/usr/bin/${py}\" "
      sudo -H sh -c "/usr/bin/${py} -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi"

      echo "upgrade_python_modules \"/usr/bin/\" \"${py}\""
      upgrade_python_modules "/usr/bin/" "${py}"
    else
      echo "    \"/usr/bin/${py}\" does not appear to be available."
    fi

    # There may be more in a virtual environment, too
    target="`which ${py}`"
    if [ ! -z "${target}" ]; then
      echo "    Found \"${target}\""
      sudo -H sh -c "${target} -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi"
      location="$( cd "$( dirname "${target}" )" >/dev/null 2>&1 && pwd )"
      upgrade_python_modules ${location} ${py}

  # http://ouimeaux.readthedocs.io/en/latest/installation.html
  # wemo wrapper in python :-)
  # python3 -m pip install ouimeaux
    else
      echo "    ${i} does not appear to be available."
    fi
  done

}

enumerate_python_versions
