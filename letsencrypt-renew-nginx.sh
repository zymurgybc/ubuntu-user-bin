#!/bin/sh
#/usr/sbin/service nginx stop  # or whatever your webserver is
#. /opt/eff.org/certbot/venv/bin/activate

GITREPO=/usr/local/src/github/letsencrypt/
cd ${GITREPO}
git pull

# the standalone method will use its own web server, so we need to stop nginx to free the ports
/usr/sbin/service nginx stop

#killall nginx

#./letsencrypt-auto renew -nvv --standalone > /var/log/letsencrypt/renew_$(date -d "today" +"%Y%m%d%H%M").log 2>&1
./letsencrypt-auto renew -nvv --standalone > /var/log/letsencrypt/renew.log 2>&1

LE_STATUS=$?
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

