#!/bin/bash
# https://community.home-assistant.io/t/python-3-9-install-on-raspberry-pi-os/241558

sudo apt update

sudo apt upgrade -y

version=3.9.6
wget https://www.python.org/ftp/python/$version/Python-$version.tar.xz  -O /tmp/Python-$version.tar.xz 

# Extract, build and install from source tarball
cd /tmp

tar xf Python-$version.tar.xz

cd Python-$version

./configure --enable-optimizations

sudo make altinstall

sudo apt -y autoremove

# Connect the local build components to the "usual suspects" location
sudo ln -s /usr/local/bin/python3.9 /usr/bin/python3.9
sudo ln -s /usr/local/bin/python3.9-config /usr/bin/python3.9-config

# Ensure the pip is properly updated
sudo /usr/bin/python3.9 -m pip install --upgrade pip

# Clean up the temporary file bits
cd

sudo rm -rf /tmp/Python-$version

rm /tmp/Python-$version.tar.xz
