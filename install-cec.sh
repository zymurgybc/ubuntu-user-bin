#!/bin/bash
sudo apt-get install build-essential autoconf liblockdev1-dev libudev-dev git libtool pkg-config
cd ~/source/github.com
if [ ! -d "Pulse-Eight" ]; then
   mkdir Pulse-Eight
fi
cd Pulse-Eight

# =========================
if [ ! -d "platform" ]; then
   git clone git://github.com/Pulse-Eight/platform.git
fi

cd platform
cd libcec
git pull

if [ ! -d "build" ]; then
   mkdir build
fi

cd build
cmake ..
make -j4
sudo make install

# =========================
cd ~/source/github.com/Pulse-Eight/

if [ ! -d "libcec" ]; then
   git clone git://github.com/Pulse-Eight/libcec.git
fi

cd libcec
git pull

if [ ! -d "build" ]; then 
   mkdir build
fi

cd build
cmake ..
make -j4
sudo make install
sudo ldconfig

cec-client -l

