#!/bin/bash

cd ~/bin

git config --global user.email "zymurgy.bc@gmail.com"
git config --global user.name "Ted H."
git config --global push.default simple
git config --global core.editor "nano"
git config --global credential.helper cache
git pull

sudo apt-get -y update
sudo apt-get -y install aptitude curl mailutils cmake ssmtp
sudo apt-get -y install mosquitto-clients build-essential jq \
                        python3-pip matchbox-keyboard  libnss-myhostname  \
                        autoconf automake bison libtool libffi-dev \
                        ruby ruby-dev gem

sudo apt-get -y install pkgconf gobject-introspection libgirepository1.0-dev \
                        libcairo2 libcairo-dev
#python-dev python-pip libpython-dev \
#libpython2.7-dev python2.7-dev libpython-dev libpython2.7-dev \
#python-dev python2.7-dev

sudo apt-get -y install swig swig2.0.*
sudo aptitude -y install nfs-kernel-server nfs-common portmap dos2unix libssl-dev libtiff5-dev \
                         zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev \
                         tcl tcl8.6 tcl8.6-dev tk8.6-dev python3-tk

sudo update-rc.d rpcbind enable
sudo service rpcbind start
sudo modprobe ipv6

## ------------ Ensure some basics in Ruby
sudo gem install require json httpclient colorize
sudo gem update --system

if [ ! -f "${HOME}/dead.letter" ]; then
    touch ${HOME}/dead.letter
    sudo cp ~/bin/etc_config/etc_mail.rc /etc/mail.rc
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
    scp theather@wasabi:~/.ssh/config ~/.ssh/
fi

if [ ! -f "${HOME}/bin/dyndns-update.config" ]; then
    echo Getting a copy of ~/bin/dyndns-update.config
    scp theather@wasabi:~/bin/dyndns-update.config ~/bin/
fi

if [ ! -f "${HOME}/bin/myip.cronmail.config" ]; then
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

sudo perl -MCPAN -e "install 'CPAN::DistnameInfo'; install 'YAML'; install 'CPAN'" #; reload CPAN"
sudo perl -MCPAN -e 'my $c = "CPAN::HandleConfig"; $c->load(doit => 1, autoconfig => 1); $c->edit(prerequisites_policy => "follow"); $c->edit(build_requires_install_policy => "yes"); $c->commit'
@ Updates to run dhsupdate.pl
sudo perl -MCPAN -e "install 'Net::SSLeay'; 'IO::Socket::SSL'; 'IO::Socket::SSL::Utils'; 'LWP::Protocol::https'; install 'LWP::Simple'; 'LWP:UserAgent'; "

if [ -f "${HOME}/bin/upgrade-python.sh" ]; then
    ${HOME}/bin/upgrade-python.sh
fi

sudo apt-get -y clean && \
sudo apt-get -y autoremove && \
sudo apt     -y autoremove

