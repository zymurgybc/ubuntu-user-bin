   sudo apt-get update          \
&& sudo apt-get -y upgrade      \
&& sudo apt-get -y dist-upgrade \
&& sudo apt-get -y purge libreoffice wolfram-* sonic-pi scratch flashplugin-installer 2>/dev/null \
&& sudo apt-get -y autoremove   \
&& sudo apt     -y autoremove

verPython=("python2.7" "python3.4" "python3.5" "python3.6" "python3.7" )
for i in "${verPython[@]}"
do
    echo "Checking for ${i}..."
    if [ ! -z "`which ${i}`" ]; then
        echo "    Found \"`which ${i}`\""
        sudo -H sh -c "`which ${i}` -m pip install --upgrade pip ephem pytz pika python-dateutil tendo paho-mqtt cffi smbus-cffi"
# http://ouimeaux.readthedocs.io/en/latest/installation.html
# wemo wrapper in python :-)
# python3 -m pip install ouimeaux
    else
        echo "    ${i} does not appear to be available."
    fi
done

#echo upgrade | sudo -H cpan
#echo upgrade | cpan
