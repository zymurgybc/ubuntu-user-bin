/****** zway-mqtt bridge **************************************************************/
// adapted from  http://wetwa.re/?p=136
// imported into  /opt/z-way-server/automation/main.js on razberry

var mqtt_config = fs.loadJSON("mqtt_config.json") || [];
var mqtt_topic_prefix = 'home/zwave/'; 

// Here the 20 and 21 are hardcoded Z-Wave device ID's for wall plugs/power switches. 
// Change them accordingly to your setup 
var switches = (function() { 
    var switches = ['binary', 'dimmer'];
    switches['binary'] = [];
    switches['dimmer'] = [];

    for(var id in zway.devices)
    {
        if(zway.devices.hasOwnProperty(id) && (typeof zway.devices[id].instances[0].commandClasses[37] != 'undefined'))
        {
            switches['binary'].push(id);
        }

        if(zway.devices.hasOwnProperty(id) && (typeof zway.devices[id].instances[0].commandClasses[38] != 'undefined'))
        {
            switches['dimmer'].push(id);
        }
    }
    return switches;
})();
 
function publish_mqtt (topic, value) {
    try {
        console.log("ZWay-Mqtt plugin publishing \"" +  mqtt_topic_prefix + topic + "\" with value \"" + value + "\" to host " + mqtt_config["mqtt_host"]);
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
            value || "null",
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
    //value = 'on';
    if (theValue == false){
        state = 'off';
        //value = 'off';
    }
    eventString = 'Device' + device + "/value";
    publish_mqtt(eventString, state);
}

function switch_multilevel (device, instance, theValue) {
    console.log("MQTT plugin: dev#" + device + " (dimmer switch): " + theValue)
    //state = 'on';
    value = '99';
    if (theValue == false){
        //state = 'off';
        value = '0';
    }
    eventString = 'Device' + device + "/value";
    publish_mqtt(eventString, value);
}

function switch_binary_meter (device, instance, theValue) {
    console.log("MQTT plugin: dev#" + device + " (binary switch meter): " + theValue)
    eventString = 'Device' + device + "/meter";
    publish_mqtt(eventString, theValue);
}

// Publish some information config to MQTT
function publish_info(zway, devid) {
    if(typeof(zway.devices[ devid ].data) != 'undefined') {
        if(typeof(zway.devices[ devid ].data.givenName) != 'undefined') {
            descr_topic = "Device" + devid + "/name";
            descr_value = zway.devices[ devid ].data.givenName.value;
            publish_mqtt(descr_topic, descr_value);
            console.log("MQTT plugin: register device name \"" + descr_value + "\"");
        }
    }

    descr_topic = "Device" + devid + "/type";
    if(zway.devices[ devid ].instances[0].SwitchMultiLevel != 'undefined') {
        descr_value = 'SwitchMultilevel';
        publish_mqtt(descr_topic, descr_value);
        console.log("MQTT plugin: register device as type \"" + descr_value + "\"");
    } else 
    if(zway.devices[ devid ].instances[0].SwitchBinary != 'undefined') {
        descr_value = 'SwitchBinary';
        publish_mqtt(descr_topic, descr_value);
        console.log("MQTT plugin: register device as type \"" + descr_value + "\"");
    }
}

console.log("MQTT plugin: found " + switches['binary'].length + " binary switches");
console.log("MQTT plugin: found " + switches['dimmer'].length + " dimmer switches");

for (var i=0; i < switches.length; i++) {
    var group = switches[i]
    for(var t=0; t < switches[i].length; t++) {
        
        var id = switches[group][t];
        // create and add an event listener
        (function(devid) {
            console.log("MQTT plugin: Configure power switch " + devid);
            if(typeof(zway.devices[ devid ]) != 'undefined') {
                if(typeof(zway.devices[ devid ].instances[0].SwitchBinary) != 'undefined') {
                    zway.devices[ devid ].instances[0].SwitchBinary.data.level.bind(function() {
                       switch_binary (devid, 0, this.value);
                    });
                }

                if(typeof(zway.devices[ devid ].instances[0].SwitchMultiLevel) != 'undefined') {
                    zway.devices[ devid ].instances[0].SwitchMultiLevel.data.level.bind(function() {
                        switch_multilevel (devid, 0, this.value);
                    });
                }

                if(typeof(zway.devices[ devid ].instances[0].Meter) != 'undefined') {
                    zway.devices[ devid ].instances[0].Meter.data.val.bind(function() {
                        switch_binary_meter (id, 0, this.value);
                    });
                }

                publish_info(zway, id);
            } else {
                console.log("MQTT plugin: Invalid device id " + devid);
            }

        })(id); // tie device ID so it is referenced correctly from callback funcs
    }
}
