#!/bin/bash

if [ ! -d "/home/pi/.ssh/" ]; then
    ssh-keygen -t ecdsa
fi

cd ~/bin

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."
git config --global push.default simple
git pull

sudo apt-get install curl mailutils ssmtp mosquitto-clients jq

sudo cp ~/bin/etc_config/etc_mail.rc /etc/mail.rc

if [ ! -f "/home/pi/dead.letter" ]; then
    touch /home/pi/dead.letter
fi

if [ ! -f "/home/pi/.ssh/config" ]; then
    echo Getting a copy of ~/.ssh/config
    scp theather@wasabi:~/.ssh/config /home/pi/.ssh/
fi

if [ ! -f "/home/bin/dyndns-update.config" ]; then
    echo Getting a copy of ~/bin/dyndns-update.config
    scp theather@wasabi:~/bin/dyndns-update.config /home/pi/bin/
fi

if [ ! -f "/home/pi/bin/myip.cronmail.config" ]; then
    echo Getting a copy of ~/bin/myip.cronmail.config
    scp theather@wasabi:~/bin/myip.cronmail.config ~/bin/
fi

if [ ! -f "/var/log/myip.log" ]; then
    sudo touch /var/log/myip.log
fi

if [ ! -f "/home/pi/bin/mqtt_config.json" ]; then
    echo Getting a copy of ~/bin/mqtt_config.json
    scp theather@wasabi:~/bin/mqtt_config.json ~/bin/
fi

if [ -f "/home/pi/bin/crontab.`hostname`.bak" ]; then
    sudo crontab /home/pi/bin/crontab.`hostname`.bak
fi

