#!/bin/bash

cd ~/bin

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."
git config --global push.default simple
git config --global core.editor "nano"
git pull

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install aptitude curl mailutils cmake ssmtp mosquitto-clients jq python-dev \
                     python-pip python3-pip matchbox-keyboard libnss-myhostname \
                     autoconf libtool automake bison swig swig2.0
sudo aptitude install nfs-kernel-server nfs-common portmap dos2unix libssl-dev libtiff4-dev \
                     zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk

sudo update-rc.d rpcbind enable
sudo service rpcbind start

sudo cp ~/bin/etc_config/etc_mail.rc /etc/mail.rc

sudo modprobe ipv6

if [ ! -f "${HOME}/dead.letter" ]; then
    touch ${HOME}/dead.letter
fi
## ----------- Configure SSH
if [ ! -d "${HOME}/.ssh" ]; then
    mkdir "$HOME/.ssh"
fi
chmod -R 700 "${HOME}/.ssh"

if [ ! -f "${HOME}/.ssh/id_ecdsa" ]; then
    ssh-keygen -t ecdsa
fi

if [ ! -f "${HOME}/.ssh/id_rsa" ]; then
    ssh-keygen -t rsa
fi

if [ ! -f "${HOME}/.ssh/config" ]; then
    echo Getting a copy of ~/.ssh/config
    scp theather@wasabi:~/.ssh/config /home/pi/.ssh/
fi

if [ ! -f "/home/pi/bin/dyndns-update.config" ]; then
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

if [ ! -f "${HOME}/bin/mqtt_config.json" ]; then
    echo Getting a copy of ~/bin/mqtt_config.json
    scp theather@wasabi:~/bin/mqtt_config.json ~/bin/
fi

if [ -f "${HOME}/bin/crontab.`hostname`.bak" ]; then
    sudo crontab ~/bin/crontab.`hostname`.bak
fi

sudo perl -MCPAN -e 'my $c = "CPAN::HandleConfig"; $c->load(doit => 1, autoconfig => 1); $c->edit(prerequisites_policy => "follow"); $c->edit(build_requires_install_policy => "yes"); $c->commit'
sudo -H pip install --upgrade ephem pytz pika python-dateutil 
sudo python2.7 -m pip install --upgrade tendo paho-mqtt
sudo python3.4 -m pip install --upgrade tendo paho-mqtt

sudo apt-get clean && sudo apt-get autoremove
