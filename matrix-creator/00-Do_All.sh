#!/bin/bash
# http://jasperproject.github.io/documentation/installation/

LOGFILE=$HOME/bin/matrix-creator/00-Do_All.log

# sudo nano /etc/modprobe.d/alsa-base.conf
# - Change the following line:
# - options snd-usb-audio index=-2
# + To this:
# + options snd-usb-audio index=0
# sudo alsa force-reload

# Add the following line to the end of ~/.bash_profile
# export LD_LIBRARY_PATH="/usr/local/lib"
# source .bashrc


# And this to your ~/.bashrc or ~/.bash_profile:
# LD_LIBRARY_PATH="/usr/local/lib"
# export LD_LIBRARY_PATH
# PATH=$PATH:/usr/local/lib/
# export PATH


source 10-Add-Package-Repos
source 10-NodeRed-UpgradeInstallation
source 20-Clone_GitHub-MatrixIO
source 20-GetJasperProject

#source matrix_alexa.sh
