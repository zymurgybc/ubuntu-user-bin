# https://forums.raspberrypi.com/viewtopic.php?t=75137
# Apr 2024

TEST_LOG=/var/log/check_network.log
ping -c4 192.168.73.1 | ts '[\%Y-\%m-\%d \%H:\%M:\%S]' >> ${TEST_LOG}

if [ $? != 0 ]
then
  echo ========== Restarting Network  | ts '[\%Y-\%m-\%d \%H:\%M:\%S]' >> ${TEST_LOG}
  sudo ifconfig wlan0 down | ts '[\%Y-\%m-\%d \%H:\%M:\%S]' >> ${TEST_LOG}
  sleep 5
  sudo ifconfig wlan0 up   | ts '[\%Y-\%m-\%d \%H:\%M:\%S]' >> ${TEST_LOG}
fi
