#!/bin/bash
# http://mikegrouchy.com/blog/2014/06/pro-tip-pip-upgrade-all-python-packages.html
# pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install --upgrade


for py in `ls /usr/bin/python?.?`; do
  sudo $py -m pip install --upgrade freeze pip
  $py -m pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | sudo xargs $py -m pip install --upgrade
done
