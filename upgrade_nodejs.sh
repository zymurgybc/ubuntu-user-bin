#!/bin/bash
# http://davidwalsh.name/upgrade-nodejs
sudo npm cache clean -f
sudo npm install -g n
sudo n stable
echo Now running node.js version `node -v`
