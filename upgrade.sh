   sudo apt-get update          \
&& sudo apt-get -y upgrade      \
&& sudo apt-get -y dist-upgrade \
&& sudo apt-get -y purge libreoffice wolfram-* sonic-pi scratch flashplugin-installer 2>/dev/null \
&& sudo apt-get -y autoremove   \
&& sudo apt     -y autoremove

#echo upgrade | sudo -H cpan
#echo upgrade | cpan
