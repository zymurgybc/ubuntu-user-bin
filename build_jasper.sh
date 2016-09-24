#!/bin/bash
# http://jasperproject.github.io/documentation/installation/

LOGFILE=$HOME/bulid_jasper.log

sudo apt-get update        2>&1 | tee    $LOGFILE
sudo apt-get upgrade --yes 2>&1 | tee -a $LOGFILE
# sudo apt-get install nano git-core python-dev python-pip subversion autoconf libtool automake gfortran g++ --yes
echo "sudo apt-get install bison libasound2-dev libportaudio-dev python-pyaudio --yes" 2>&1 | tee -a $LOGFILE
sudo apt-get install bison libasound2-dev libportaudio-dev python-pyaudio --yes 2>&1 | tee -a $LOGFILE

# Google  and Ivona Text-to-speech
echo "sudo apt-get install --upgrade python-pymad --yes"     2>&1 | tee -a $LOGFILE
sudo apt-get install --upgrade python-pymad --yes            2>&1 | tee -a $LOGFILE
echo "sudo pip3    install --upgrade gTTS gtts-token pyvona" 2>&1 | tee -a $LOGFILE
sudo pip3    install --upgrade gTTS gtts-token pyvona        2>&1 | tee -a $LOGFILE

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


echo "cd && cd source/github.com" 2>&1 | tee -a $LOGFILE
cd && cd source/github.com
if [ !-d "jasperproject" ]; then
  echo "mkdir jasperproject" 2>&1 | tess -a $LOGFILE
  mkdir jasperproject
fi

cd jasperproject

if [ !-d "jasper" ]; then
  echo "git clone https://github.com/jasperproject/jasper-client.git jasper"  2>&1 | tee -a $LOGFILE
  git clone https://github.com/jasperproject/jasper-client.git jasper  2>&1 | tee -a $LOGFILE
fi

echo "cd jasper" 2>&1 | tee -a $LOGFILE
cd jasper
echo "in Jasper ... git pull"  2>&1 | tee -a $LOGFILE
git pull  2>&1 | tee -a $LOGFILE

echo 2>&1 | tee -a $LOGFILE
echo "# if you get error installing Jasper, try this..." 2>&1 | tee -a $LOGFILE
echo "# http://stackoverflow.com/questions/27341064/how-do-i-fix-importerror-cannot-import-name-incompleteread" 2>&1 | tee -a $LOGFILE
echo "#sudo apt-get remove python-pip python3-pip" 2>&1 | tee -a $LOGFILE
echo "#sudo python  -measy_install pip"  2>&1 | tee -a $LOGFILE
echo "#sudo python3 -measy_install pip"  2>&1 | tee -a $LOGFILE
echo 2>&1 | tee -a $LOGFILE

# Jasper requires various Python libraries that we can install in one line with:
echo "sudo pip3 install --upgrade setuptools"       2>&1 | tee -a $LOGFILE
sudo pip3 install --upgrade setuptools              2>&1 | tee -a $LOGFILE
echo "sudo pip3 install -r client/requirements.txt" 2>&1 | tee -a $LOGFILE
sudo pip3 install -r client/requirements.txt        2>&1 | tee -a $LOGFILE

# Sometimes it might be neccessary to make jasper.py executable:
echo "chmod +x jasper.py" 2>&1 | tee -a $LOGFILE
chmod +x jasper.py        2>&1 | tee -a $LOGFILE

# To be able to understand what you say, Jasper still needs a Speech-to-Text (STT) engine. 
# Jasper also needs a Text-to-Speech (TTS) engine to answer to your commands.

echo "sudo apt-get install --upgrade pocketsphinx --yes" 2>&1 | tee -a $LOGFILE
sudo apt-get install --upgrade pocketsphinx --yes        2>&1 | tee -a $LOGFILE

cd ~/source

if [ !-d "code.sf.net" ]; then
  mkdir code.sf.net 2>&1 | tee -a $LOGFILE
fi

cd code.sf.net

if [ !-d "cmusphinx" ]; then
  mkdir cmusphinx 2>&1 | tee -a $LOGFILE
fi

cd cmusphinx

if [ !-d "cmuclmtk" ]; then
  svn co https://svn.code.sf.net/p/cmusphinx/code/trunk/cmuclmtk/ 2>&1 | tee -a $LOGFILE
fi

cd cmuclmtk/
./autogen.sh && make && sudo make install 2>&1 | tee -a $LOGFILE
cd ..

# On Raspian, you can install these from the experimental repository:
#sudo su -c "echo 'deb http://ftp.debian.org/debian experimental main contrib non-free' > /etc/apt/sources.list.d/experimental.list"
#sudo apt-get update
#sudo apt-get -t experimental install phonetisaurus m2m-aligner mitlm libfst-tools

