#!/bin/bash 
VERSION=`date +"%Y-%m-%d"`
KEY_FILE="`hostname`.mqtt-server.${VERSION}.key.pem"
CSR_FILE="`hostname`.mqtt-server.${VERSION}.csr.pem"

openssl req -new \
        -newkey rsa:2048 -keyout /etc/mosquitto/certs/${KEY_FILE} -sha256 -nodes \
        -subj "/C=CA/ST=British Columbia/L=Victoria/O=Heatherington Residence/OU=Heatherington/CN=`hostname`/emailAddress=zymurgy.bc@gmail.com/subjectAltName=DNS.1=`hostname`.penrose.newtonian.ca,DNS.2=`hostname`.local" \
        -out /etc/mosquitto/certs/${CSR_FILE}
