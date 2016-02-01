#!/bin/bash 
# http://blog.endpoint.com/2014/10/openssl-csr-with-alternative-names-one.html
# https://www.openssl.org/docs/manmaster/apps/req.html

VERSION=`date +"%Y-%m-%d-%H%M%S"`
KEY_FILE="`hostname`.mqtt-server.${VERSION}.key.pem"
CSR_FILE="`hostname`.mqtt-server.${VERSION}.csr.pem"
CERT_FILE="`hostname`.mqtt-server.${VERSION}.cert.pem"
CERT_FOLDER=/etc/mosquitto/certs/

openssl req -new \
        -newkey rsa:2048 -keyout ${CERT_FOLDER}/${KEY_FILE} -sha256 -nodes \
        -subj "/C=CA/ST=British Columbia/L=Victoria/O=Heatherington Residence/OU=Heatherington/CN=`hostname`/emailAddress=zymurgy.bc@gmail.com/subjectAltName=DNS.1=`hostname`.penrose.newtonian.ca,DNS.2=`hostname`.local" \
        -out ${CERT_FOLDER}/${CSR_FILE}


# https://jamielinux.com/docs/openssl-certificate-authority/sign-server-and-client-certificates.html
cd /root/ca
openssl ca -config intermediate/openssl.cnf \
      -extensions server_cert -days 375 -notext -md sha256 \
      -in ${CERT_FOLDER}/${CSR_FILE} \
      -out ${CERT_FOLDER}/${CERT_FILE}

chmod 444 ${CERT_FOLDER}/${CERT_FILE}
