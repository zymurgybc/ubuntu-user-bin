   sudo apt-get update          \
&& sudo apt-get -y upgrade      \
&& sudo apt-get -y dist-upgrade \
&& sudo apt-get -y purge libreoffice wolfram-* sonic-pi scratch flashplugin-installer 2>/dev/null \
&& sudo apt-get -y autoremove   \
&& sudo apt     -y autoremove

mkdir -p "${HOME}/tmp"

if [ -f "${HOME}/bin/upgrade-python.sh" ]; then
    if [ -f "${HOME}/tmp/upgrade-python.log" ]; then
        rm "${HOME}/tmp/upgrade-python.log"
    fi
    ${HOME}/bin/upgrade-python.sh | tee -a ${HOME}/tmp/upgrade-python.log
fi

if [ -f "${HOME}/bin/upgrade.${HOSTNAME}.sh" ]; then
    if [ -f "${HOME}/tmp/upgrade.${HOSTNAME}.log" ]; then
        rm "${HOME}/tmp/upgrade.${HOSTNAME}.log"
    fi
    . "${HOME}/bin/upgrade.${HOSTNAME}.sh" 2>&1 | tee -a "${HOME}/tmp/upgrade.${HOSTNAME}.log"
fi

#echo upgrade | sudo -H cpan
#echo upgrade | cpan
