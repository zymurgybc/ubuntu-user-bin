#!/bin/bash

if [ ! -d "~/.ssh" ]; then
    ssh-keygen -t ecdsa
fi

cd ~/bin

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."
git pull

sudo apt-get install curl mailutils ssmtp mosquitto-clients

sudo cp ~/bin/etc_config/etc_mail.rc /etc/mail.rc

if [ ! -f "~/dead.letter" ]; then
    touch ~/dead.letter
fi

if [ ! -f "~/.ssh/config" ]; then
    echo Getting a copy of ~/.ssh/config
    scp theather@wasabi:~/ssh/config ~/.ssh/
fi

if [ ! -f "~/bin/dyndns-update.config" ]; then
    echo Getting a copy of ~/bin/dyndns-update.config
    scp theather@wasabi:~/bin/dyndns-update.config ~/bin/
fi

if [ ! -f "~/bin/myip.cronmail.config" ]; then
    echo Getting a copy of ~/bin/myip.cronmail.config
    scp theather@wasabi:~/bin/myip.cronmail.config ~/bin/
fi

if [ ! -f "/var/log/myip.log" ]; then
    sudo touch /var/log/myip.log
fi

if [ -f "~/bin/crontab.`hostname`.bak" ]; then
    sudo crontab /home/pi/bin/crontab.`hostname`.bak
fi
