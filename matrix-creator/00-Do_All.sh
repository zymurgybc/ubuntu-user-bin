#!/bin/bash
# http://jasperproject.github.io/documentation/installation/

_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
LOGFILE=$_dir/00-Do_All.log

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

cd $_dir
source 10-Add-Package-Repos | tee -a 10-Add-Package-Repos.log

cd $_dir
source 10-NodeRed-UpgradeInstallation | tee -a 10-NodeRed-UpgradeInstallation.log

cd $_dir
source 20-Clone_GitHub-Google | tee -a 20-Clone_GitHub-Google.log

cd $_dir
source 20-Clone_GitHub-MatrixIO | tee -a 20-Clone_GitHub-MatrixIO.log

cd $_dir
source 30-Face-analytics | tee -a  30-Face-analytics.log

cd $_dir
source 30-Matrix-app-config-helper | tee -a 30-Matrix-app-config-helper.log
cd $_dir
source 30-Matrix-cli

cd $_dir
source matrix-io.github.io

cd $_dir
source 30-Matrix-creator-case

cd $_dir
source 30-Matrix-app-clickgames

cd $_dir
source 30-Matrix-cv

cd $_dir
source 30-Matrix-srcjs-apps

cd $_dir
source 30-Matrix-creator-malos-android

cd $_dir
source 30-protocol-buffers

cd $_dir
source 30-Matrix-continuity

cd $_dir
source 30-Matrix-creator-alexa-voice-demo

cd $_dir
source 30-Matrix-creator-alexa-voice-services

cd $_dir
source 30-Matrix-creator-documentation

cd $_dir
source 30-Matrix-docs-templates

cd $_dir
source 30-Matrix-creator-fpga

cd $_dir
source 30-Matrix-creator-hal

cd $_dir
source 30-Matrix-creator-init

cd $_dir
source 30-Matrix-creator-malos

cd $_dir
source 30-Matrix-creator-uv-demo

cd $_dir
source 30-Matrix-OS

cd $_dir
source 30-Matrix-TV-Remote

cd $_dir
source 50-GetJasperProject

#cd $_dir
#source matrix_alexa.sh
