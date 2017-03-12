#!/bin/bash

sudo apt-get install autogen autoconf libtool automake swig swig2.0 bison

cd /opt
if [ ! -d "cmusphinx" ]; then
    sudo mkdir cmusphinx
    sudo chown pi.pi cmusphinx
fi

cd cmusphinx

if [ ! -d "sphinxbase" ]; then
    git clone https://github.com/cmusphinx/sphinxbase
fi

cd sphinxbase

git pull

if [ ! -f "configure" ]; then
  ./autogen.sh
fi

./configure --enable-fixed --without-lapack
#    --prefix=/my/own/installation/directory
make clean all
make check
sudo make install

cd ..
if [ ! -d "pocketsphinx" ]; then
    git clone https://github.com/cmusphinx/pocketsphinx
fi

cd pocketsphinx

git pull

if [ ! -f "configure" ]; then
  ./autogen.sh
fi

./configure --enable-fixed --without-lapack
#    --prefix=/my/own/installation/directory
make clean all
make check
sudo make install

cd ..
