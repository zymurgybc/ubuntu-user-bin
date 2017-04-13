   sudo apt-get update          \
&& sudo apt-get -y upgrade      \
&& sudo apt-get -y dist-upgrade \
&& sudo apt-get -y purge libreoffice wolfram-engine sonic-pi scratch \
&& sudo apt-get -y autoremove
