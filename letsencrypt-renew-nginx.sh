#!/bin/sh
#. /opt/eff.org/certbot/venv/bin/activate

sudo certbot renew --nginx #--dry-run
exit $?

#===================================================

GITREPO=/usr/local/src/github/letsencrypt/
cd ${GITREPO}
git pull

USE_PYTHON_3=1
export USE_PYTHON_3

# the standalone method will use its own web server, so we need to stop nginx to free the ports
/usr/sbin/service nginx stop

#CERTLOG=/var/log/letsencrypt/renew_$(date -d "today" +"%Y%m%d%H%M").log
CERTLOG=/var/log/letsencrypt/renew.log

./letsencrypt-auto renew -nvv --standalone | tee -a ${CERTLOG} 2>&1

LE_STATUS=$?
echo "zz${LE_STATUS}"

/usr/sbin/service nginx start # or whatever your webserver is
if [ "$LE_STATUS" != 0 ]; then
    echo Automated renewal failed:
    if [ -f "/var/log/letsencrypt/renew.log" ]; then
        cat  /var/log/letsencrypt/renew.log
    else
        echo Log not available
    fi
    exit 1
fi


