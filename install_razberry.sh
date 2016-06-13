wget -q -O - razberry.zwave.me/install |  sudo bash

mkdir ~/tmp
cd ~/tmp
wget http://nodejs.org/dist/v0.10.25/node-v0.10.25-linux-x64.tar.gz

if [ ! -d "/opt/packages" ]; then
    sudo mkdir /opt/packages
    sudo chown -R pi.pi /opt/packages
fi
cd /opt/packages
gzip -dc ~/tmp/node-v0.10.25-linux-x64.tar.gz | tar xf -

ln -s /opt/packages/node-v0.10.25-linux-x64/ /opt/node
