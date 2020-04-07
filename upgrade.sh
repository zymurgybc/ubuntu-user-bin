   sudo apt-get update          \
&& sudo apt-get -y upgrade      \
&& sudo apt-get -y dist-upgrade \
&& sudo apt-get -y purge libreoffice wolfram-* sonic-pi scratch flashplugin-installer 2>/dev/null \
&& sudo apt-get -y autoremove   \
&& sudo apt     -y autoremove

if [ -f "${HOME}/bin/upgrade-python.sh" ]; then
    if [ -f "${HOME}/upgrade-python.log" ]; then
        rm "${HOME}/upgrade-python.log"
    fi
    ${HOME}/bin/upgrade-python.sh | tee -a ${HOME}/upgrade-python.log
fi

#echo upgrade | sudo -H cpan
#echo upgrade | cpan
