#!/usr/bin/env python3
# https://gist.github.com/mdrovdahl/0af14b84da43fb1801fe212ffc5ff30c

import requests, os, json

config_json = os.path.dirname(os.path.realpath(__file__)) + '/neviweb.json'
with open(config_json, 'r') as f:
    config = json.load(f)

# TODO make this the login() function
uri = config["server"]
path = 'api/login'
payload = {'email': config["email"], 'password': config["password"], 'stayConnected': '0'}

r = requests.post(uri+path, data=payload) 
result = r.json()

# TODO To check that a request is successful, use r.raise_for_status()
# or check r.status_code is what you expect.
# TODO make this the gatewayID() function

uri = config["server"]
path = 'api/gateway'
headers = {'Session-Id': result['session']}
r = requests.get(uri+path, headers=headers)
gatewayList = r.json()

# TODO if no gatetway, throw an error and logout
# TODO make this the deviceID() function
uri = config["server"]
path = 'api/device'
payload = {'gatewayId': gatewayList[0]['id']}
r = requests.get(uri+path, headers=headers, params=payload)
devices = r.json()

# TODO if no devices, throw an error and logout
# TODO make this a generic formatTemp(temp,format) function
def cToF(temp):
    return (str((9.0/5.0*float(temp)+32)))

# TODO make this the generic deviceData() function
uri = config["server"]

for device in devices:
	path = 'api/device/'+str(device['id'])+'/data?force=1'
	r = requests.get(uri+path, headers=headers)
	deviceData = r.json()
	print( "Thermostat: ", device['name'])
	#print "Temperature: " + cToF(deviceData['temperature'])
	print( "Temperature: ", deviceData['temperature'])
	#print "Setpoint: "+ cToF(deviceData['setpoint'])
	print( "Setpoint: ", deviceData['setpoint'])

