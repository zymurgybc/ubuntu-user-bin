#!/usr/bin/bash
# http://jasperproject.github.io/documentation/installation/

sudo apt-get update
sudo apt-get upgrade --yes
# sudo apt-get install nano git-core python-dev python-pip subversion autoconf libtool automake gfortran g++ --yes
sudo apt-get install bison libasound2-dev libportaudio-dev python-pyaudio --yes

# Google  and Ivona Text-to-speech
sudo apt-get install python-pymad --yes
sudo pip install --upgrade gTTS pyvona

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


cd && cd Source/gitgub.com
if [ !-d "jasperproject" ]; then
  mkdir jasperproject
fi

cd jasperproject

if [ !-d "jasper" ]; then
  git clone https://github.com/jasperproject/jasper-client.git jasper
fi

cd jasper
git pull

# Jasper requires various Python libraries that we can install in one line with:
sudo pip install --upgrade setuptools
sudo pip install -r client/requirements.txt

# Sometimes it might be neccessary to make jasper.py executable:
chmod +x jasper.py

# To be able to understand what you say, Jasper still needs a Speech-to-Text (STT) engine. 
# Jasper also needs a Text-to-Speech (TTS) engine to answer to your commands.

sudo apt-get install pocketsphinx

cd ~/Source

if [ !-d "code.sf.net" ]; then
  mkdir code.sf.net
fi

cd code.sf.net

if [ !-d "cmusphinx" ]; then
  mkdir cmusphinx
fi

cd cmusphinx


if [ !-d "cmuclmtk" ]; then
  svn co https://svn.code.sf.net/p/cmusphinx/code/trunk/cmuclmtk/
fi

cd cmuclmtk/
./autogen.sh && make && sudo make install
cd ..

# On Raspian, you can install these from the experimental repository:
#sudo su -c "echo 'deb http://ftp.debian.org/debian experimental main contrib non-free' > /etc/apt/sources.list.d/experimental.list"
#sudo apt-get update
#sudo apt-get -t experimental install phonetisaurus m2m-aligner mitlm libfst-tools

