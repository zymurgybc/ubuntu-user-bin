#!/bin/bash
# http://mikegrouchy.com/blog/2014/06/pro-tip-pip-upgrade-all-python-packages.html
# pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install --upgrade


for py in `ls /usr/bin/python?.?`; do
  sudo -H $py -m pip install --upgrade freeze pip
  $py -m pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | sudo -H xargs $py -m pip install --upgrade
done

venv = (/usr /opt/AlexaPi/src/env2.7 /opt/AlexaPi/src/env3.5)
for py in venv; do
  sudo -H $py -m pip install --upgrade freeze pip
  $py -m pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | sudo -H xargs $py -m pip install --upgrade
done
