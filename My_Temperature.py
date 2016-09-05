#!/usr/bin/env python

import sys
import os
import json
import time
import datetime
import requests
import traceback

from grovepi import grovepi


# temp_humidity_sensor_type
# Grove Base Kit comes with the blue sensor.
BLUE = 0    # The Blue colored sensor.
WHITE = 1   # The White colored sensor.

GROVE_SENSOR = 4

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 10

#print 'Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS)
#print 'Press Ctrl-C to quit.'

while True:
    # Attempt to get sensor reading.
    # humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
    [temp,humidity] = grovepi.dht(GROVE_SENSOR,BLUE)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    if humidity is None or temp is None:
        time.sleep(2)
        continue
        #exit(1)

    print("temp = %.02f C humidity =%.02f%%"%(temp, humidity * 10))
    time.sleep(FREQUENCY_SECONDS)
 
