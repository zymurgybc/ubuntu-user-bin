sudo apt-get install ssmtp mailutils build-essential ca-certificates
sudo apt-get install golang git mercurial
sudo apt-get install python-dev python-openssl python-pip python3-pip
sudo apt-get install libusb-dev libasound2-dev libice-dev libftdi-dev libsm-dev libx11-dev libirman-dev libxt-dev libsm-dev libx11-dev libirman-dev libxt-dev libffi-dev
sudo apt-get source lirc

#wget -q -O - razberry.z-wave.me/install | sudo bash

sudo crontab /home/pi/bin/crontab.razberry.bak

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."


if [ ! -d "/home/pi/Source" ]; then
  mkdir /home/pi/Source
fi

export GOPATH="/usr/local/src/go/"
if [ ! -d "$GOPATH" ]; then
    sudo mkdir $GOPATH
fi
sudo chown pi.pi -R $GOPATH

cd /home/pi/Source/go
sudo -E go get -u github.com/odeke-em/drive/cmd/drive


# ensure the latest; Python 2.7 basic install seems OLD
sudo pip install --upgrade pyasn1
sudo pip install --upgrade tendo paho-mqtt smbus-cffi grovepi rpi.gpio adafruit-bmp adafruit-gpio
if [ ! -d "/home/pi/Source/python" ]; then
  mkdir /home/pi/Source/python
fi

if [ ! -d "/home/pi/Source/python/Adafruit_Python_DHT" ]; then
  cd /home/pi/Source/python/
  git clone https://github.com/adafruit/Adafruit_Python_DHT.git
fi

cd /home/pi/Source/python/Adafruit_Python_DHT
git pull

sudo python setup.py install



if [ ! -d "/home/pi/Source/python/Adafruit_Python_GPIO" ]; then
  cd /home/pi/Source/python/
  git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
fi

cd /home/pi/Source/python/Adafruit_Python_GPIO
git pull

sudo python setup.py install



if [ ! -d "/home/pi/Source/python/gspread" ]; then
  cd /home/pi/Source/python/
  git clone https://github.com/burnash/gspread.git
fi

cd /home/pi/Source/python/gspread
git pull

sudo python setup.py install


if [ ! -d "/home/pi/Source/python/oauth2client" ]; then
  cd /home/pi/Source/python
  git clone https://github.com/google/oauth2client.git
fi

cd /home/pi/Source/python/oauth2client
git pull

sudo python setup.py install

if [ ! -d "/usr/local/src" ]; then
    sudo mkdir /usr/local/src
fi

if [ ! -d "/usr/local/src/GrovePi" ]; then
    sudo git clone https://github.com/DexterInd/GrovePi /usr/local/src/GrovePi
    sudo chown pi.pi -R /usr/local/src/GrovePi
fi

if [ ! -L "grove_i2c_barometic_sensor_BMP180.py" ]; then
    ln /usr/local/src/GrovePi/Software/Python/grove_barometer_sensors/barometric_sensor_bmp180/grove_i2c_barometic_sensor_BMP180.py /home/pi/bin/grove_i2c_barometic_sensor_BMP180.py
fi

if [ ! -L "Adafruit_I2C.py" ]; then
    ln /usr/local/src/GrovePi/Software/Python/grove_barometer_sensors/barometric_sensor_bmp180/Adafruit_I2C.py /home/pi/bin/Adafruit_I2C.py
fi

cd /usr/local/src/GrovePi
git pull


# wget -q -O - razberry.z-wave.me/install | sudo bash
