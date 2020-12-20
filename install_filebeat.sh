
if [ ! -f "/etc/apt/sources.list.d/elastic-7.x.list" ]; then
  wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

  echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | \
       sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
  echo "deb https://artifacts.elastic.co/packages/oss-7.x/apt stable main" | \
       sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
fi

sudo apt-get install apt-transport-https
sudo apt-get update && sudo apt-get install filebeat
