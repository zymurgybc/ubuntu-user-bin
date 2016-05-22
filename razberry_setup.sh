sudo apt-get install ssmtp mailutils build-essential ca-certificates
sudo apt-get install golang git mercurial
sudo apt-get install python-dev python-openssl
sudo apt-get install libusb-dev libasound2-dev libice-dev libftdi-dev libsm-dev libx11-dev libirman-dev libxt-dev libsm-dev libx11-dev libirman-dev libxt-dev
sudo apt-get source lirc

#wget -q -O - razberry.z-wave.me/install | sudo bash

sudo crontab /home/pi/bin/crontab.razberry.bak

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."


if [ ! -d "/home/pi/Source" ]; then
  mkdir /home/pi/Source
fi

if [ ! -d "/home/pi/Source/python" ]; then
  mkdir /home/pi/Source/python
fi

if [ ! -d "/home/pi/Source/go" ]; then
  mkdir /home/pi/Source/go
fi




if [ ! -d "/home/pi/Source/python/Adafruit_Python_DHT" ]; then
  cd /home/pi/Source/python/
  git clone https://github.com/adafruit/Adafruit_Python_DHT.git
fi

cd /home/pi/Source/python/Adafruit_Python_DHT
git pull

sudo python setup.py install




if [ ! -d "/home/pi/Source/python/gspread" ]; then
  cd /home/pi/Source/python/
  git clone https://github.com/burnash/gspread.git
fi

cd /home/pi/Source/python/gspread
git pull

sudo python setup.py install




# ensure the latest; Python 2.7 basic install seems OLD
pip install pyasn1

if [ ! -d "/home/pi/Source/python/oauth2client" ]; then
  cd /home/pi/Source
  git clone https://github.com/google/oauth2client.git
fi

cd /home/pi/Source/python/oauth2client
git pull

sudo python setup.py install




cd /home/pi/Source/go
go get -u github.com/odeke-em/drive/cmd/drive
