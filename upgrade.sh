   sudo apt-get update          \
&& sudo apt-get -y upgrade      \
&& sudo apt-get -y dist-upgrade \
&& sudo apt-get -y purge libreoffice wolfram-* sonic-pi scratch 2>/dev/null \
&& sudo apt-get -y autoremove
