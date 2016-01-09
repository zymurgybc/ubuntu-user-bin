sudo apt-get install ssmtp mailutils build-essential ca-certificates
sudo apt-get install python-dev python-openssl

#wget -q -O - razberry.z-wave.me/install | sudo bash

sudo crontab /home/pi/bin/crontab.razberry.bak

if [ ! -d "/home/pi/Source" ]; then
  mkdir /home/pi/Source
fi

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."


if [ ! -d "/home/pi/Source/Adafruit_Python_DHT" ]; then
  cd /home/pi/Source
  git clone https://github.com/adafruit/Adafruit_Python_DHT.git
fi

cd /home/pi/Source/Adafruit_Python_DHT
git pull

sudo python setup.py install




if [ ! -d "/home/pi/Source/gspread" ]; then
  cd /home/pi/Source
  git clone https://github.com/burnash/gspread.git
fi

cd /home/pi/Source/gspread
git pull

sudo python setup.py install




# ensure the latest; Python 2.7 basic install seems OLD
pip install pyasn1

if [ ! -d "/home/pi/Source/oauth2client" ]; then
  cd /home/pi/Source
  git clone https://github.com/google/oauth2client.git
fi

cd /home/pi/Source/oauth2client
git pull

sudo python setup.py install


