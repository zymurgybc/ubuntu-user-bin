/****** zway-mqtt bridge **************************************************************/
// adapted from  http://wetwa.re/?p=136
// imported into  /etc/opt/z-way-server/automation/main.js

var mqtt_config = loadObject("../../../../../home/pi/bin/mqtt_config.json") || [];
var mqtt_topic_prefix = 'home/devices/'; 

// Here the 20 and 21 are hardcoded Z-Wave device ID's for wall plugs/power switches. 
// Change them accordingly to your setup 
var binarySwitches = (function() { 
    var switches = [];

    //for( i = 0; i <  zway.devices.length; i++)
    //{
    //    if(typeof  object.Keys(zway.devices)[i].instances[0].commandClasses[37] != 'undefined')
    //        switches.push(zway.devices[i].id)
    //}
    for(var id in zway.devices)
    {
        if(zway.devices.hasOwnProperty(id) && (typeof zway.devices[id].instances[0].commandClasses[37] != 'undefined'))
        {
            switches.push(id);
        }
    }
    return switches;
})();

var dimmerswitches = [16] 
function publish_mqtt (topic, key) {
    try {
        system(
            "mosquitto_pub",
            "-h",
            mqtt_config["mqtt_host"],
            "-p",            
            mqtt_config["mqtt_port"],
            "-u",
            mqtt_config["mqtt_client"],
            "-P",
            mqtt_config["mqtt_password"],
            "-i",
            "zway_razberry",
            "-t",
            mqtt_topic_prefix + topic,
            "-m",
            key,
            "-r"
        );
        return;
    } catch(err) {
        debugPrint("Failed to execute script system call: " + err);
    }
}

function switch_binary (device, instance, theValue) {
    console.log("MQTT plugin: dev#" + device + " (binary switch): " + theValue)
    state = 'on';
    key = 255;
    if (theValue == false){
        state = 'off';
        key = 0;
    }
    eventString = 'Device' + device + "/switch";
    publish_mqtt(eventString, state);
}

function switch_binary_meter (device, instance, theValue) {
    console.log("MQTT plugin: dev#" + device + " (binary switch meter): " + theValue)
    eventString = 'device' + device + "/meter";
    publish_mqtt(eventString, theValue);
}
console.log("MQTT plugin: found " + binarySwitches.length + " binary switches");
for (var i=0; i < binarySwitches.length; i++) {
        var id = binarySwitches[i];
        // create and add an event listener
        (function(devid) {
                console.log("MQTT plugin: Configure power switch " + devid);
                zway.devices[ binarySwitches[i] ].instances[0].SwitchBinary.data.level.bind(function() {
                        switch_binary (id, 0, this.value);
                });
                if(typeof zway.devices[ binarySwitches[i] ].instnaces[0].Meter != 'undefined') {
                        zway.devices[ binarySwitches[i] ].instances[0].Meter.data[2].val.bind(function() {
                                switch_binary_meter (id, 0, this.value);
                        });
                }
        })(id); // tie device ID so it is referenced correctly from callback funcs

        // Publish some information config to MQTT
        (function(devid) {
               if(typeof zway.devices[ binarySwitches[i] ].data != 'undefined') {
                      if(typeof zway.devices[ binarySwitches[i] ].data.givenName != 'undefined') {
                              descr_topic = "device" + devid + "/name";
                              descr_value = zway.devices[ binarySwitches[i] ].data.givenName.value;
                              publish_mqtt(descr_topic, descr_value);
                              console.log("MQTT plugin: register device name \"" + descr_value + "\"");
                      }
               }
        })(id); // tie device ID so it is referenced correctly from callback funcs
}
