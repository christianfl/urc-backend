# smarthome backend

## This backend provides a RESTful API designed for using in small smart home environments. Written in python3.

It works by listening for HTTP POST requests on ``<IP:PORT>/setValue`` with the following JSON content:

```
{
    "device": "device-name",
    "protocol": "protocol-name",
    "function": "function-name",
    "value": "value-to-set-in-function" (optional)
}
```

and then parsing the JSON. It will look up if there is a matching device file for the device (*device-name*.json) in the ``./devices`` directory. Based on the desired protocol the request is then redirected to the binding file for the protocol. It will look up if there is a matching function and value in the device file or for some bindings in the binding file itself. If the values are valid, the command specified in the device file or binding file will be executed.

### This was not intended to be very secure so use at your own risk! Validation is at this point only partly used for user input values and may not cover all cases. Validation for settings from device file is not implemented at this moment.

## Currently supported bindings

1. REST (only HTTP POST at the moment but it is trivial to support more) as the backend just uses <a href="https://requests.readthedocs.io/en/master">Requests</a>
2. MQTT (using <a href="https://www.eclipse.org/paho/clients/python/docs/">Eclipse Paho MQTT Client</a>)
3. ADB (using <a href="https://github.com/JeffLIrion/adb_shell">adb_shell</a>)

Note: This backend does not provide a way to add mqtt devices, this has to be done by the installed broker.

Adding more bindings should be relatively easy by just looking up the code of the existing ones.

## Device file

The device files are located in ``./devices``. They are JSONs and the names need to match with the device attribute of the received request. A device file can contain specifications for one device and one or more protocols. A typical device file looks like these:

### 1. ADB

Note: You have to obtain an adbkey in order to connect to the device via adb. The standard adb implementation included in most distro's repositories saves them under ``~/.android/adbkey`` after a first successful connection.

```
{
    "device": {
        "protocols": {
            "adb": {
                "ip": "192.168.1.1",
                "port": "5555",
                "adbkey_path": "bindings/adbkey"
            }
        }
    }
}
```
Example file: ./devices/adb-device.json

### 2. REST – Working example for Yamaha RX-V475

You may have a look at my <a href="https://github.com/christianfl/av-receiver-docs/">documentation of its commands</a>!

Note: Optional ``$VALUE$`` in value of ``"command"`` will be exchanged from binding file with the value given in the HTTP POST request (if successfully parsed)

```
{
    "device": {
        "protocols": {
            "rest": {
                "address": "http://Yamaha-AVR/YamahaRemoteControl/ctrl",
                "request_method": "post",
                "functions": {
                    "switch_state": {
                        "command": "<?xml version=\"1.0\" encoding=\"utf-8\"?><YAMAHA_AV cmd=\"PUT\"><Main_Zone><Power_Control><Power>$VALUE$</Power></Power_Control></Main_Zone></YAMAHA_AV>",
                        "values": ["On", "Standby"]
                    },
                    "switch_direct": {
                        "command": "<?xml version=\"1.0\" encoding=\"utf-8\"?><YAMAHA_AV cmd=\"PUT\"><Main_Zone><Sound_Video><Direct><Mode>$VALUE$</Mode></Direct></Sound_Video></Main_Zone></YAMAHA_AV>",
                        "values": ["On", "Off"]
                    },
                    "control": {
                        "command": "<?xml version=\"1.0\" encoding=\"utf-8\"?><YAMAHA_AV cmd=\"PUT\"><Main_Zone><Cursor_Control><Cursor>$VALUE$</Cursor></Cursor_Control></Main_Zone></YAMAHA_AV>",
                        "values": ["Up", "Down", "Left", "Right", "Sel", "Return"]
                    }
                }
            }
        }
    }
}
```
Example file: ./devices/rest-device.json

### 3. MQTT – Working example for <a href="https://github.com/Koenkk/zigbee2mqtt">Zigbee2MQTT</a> Innr RB250C

Note: Optional ``$VALUE$`` in value of ``"payload"`` will be exchanged from binding file with the value given in the HTTP POST request (if successfully parsed)

```
{
    "device": {
        "protocols": {
            "mqtt": {
                "topic": "topic_name",
                "functions": {
                    "switch_state": {
                        "subtopic": "set",
                        "payload": "{\"state\":\"$VALUE$\"}",
                        "values": ["on", "off"]
                    },
                    "change_brightness": {
                        "subtopic": "set",
                        "payload": "{\"brightness\":\"$VALUE$\"}",
                        "values": "permit_all"
                    },
                    "change_color": {
                        "subtopic": "set",
                        "payload": "{\"color\":{\"hex\":\"$VALUE$\"}}",
                        "values": "permit_all"
                    },
                    "change_color_temp": {
                        "subtopic": "set",
                        "payload": "{\"color_temp\":\"$VALUE$\"}",
                        "values": "permit_all"
                    }
                }
            }
        }
    }
}
```
Example file: ./devices/mqtt-device.json

### Permitted values

- ``"values": "permit_all"`` permits all values from user input. This is not recommended for security reasons but can sometimes be very convenient, e.g. for number ranges.
- ``"values": []`` prohibits all values. This is intended for functions which don't need a specific value to set. The server throws an exception if this flag is set and the POST request from the user containts a value.

## .env file

When using mqtt, a .env file in the project root folder is required. The following values are neccessary (provided with sample data):

```
# MQTT
MQTT_BROKER_ADDRESS=localhost
MQTT_CLIENT=client
MQTT_USER=mqtt
MQTT_PASSWORD=password
MQTT_ROOT_TOPIC=zigbee2mqtt
```

At this point, the .env file is only used for mqtt. But this may change at any time.

## Installing dependencies

### Python 2

``pip install flask flask-cors python-dotenv requests paho-mqtt adb-shell``

### Python 3

``pip3 install flask flask-cors python-dotenv requests paho-mqtt adb-shell``

## Starting server in dev-mode

``python app.py``

This starts the server on Port ``5000``.

## Contributing

Contributing is always very welcome. Wether it's filing bugs, fixing issues, improving the documentation or whatever. Maybe it takes some time for me to merge things because I'm focussing on a client for this backend right now. My aim is to keep this backend small and clean. There are already many applications which are doing "everything".