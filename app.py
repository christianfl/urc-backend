#!/usr/bin/env python
# coding: utf8

from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
from bindings import binding_mqtt
from bindings import binding_rest
from bindings import binding_adb
import json

app = Flask(__name__)
CORS(app)

@app.route("/setValue", methods=['POST'])
def setValue():
  # Check required parameter
  try:
    device = request.json['device']
  except:
    resp = jsonify({"status": "Required parameter device is missing"})
    resp.status_code = 404
    return resp

  try:
    protocol = request.json['protocol']
  except:
    resp = jsonify({"status": "Required parameter protocol is missing"})
    resp.status_code = 404
    return resp

  try:
    function = request.json['function']
  except:
    resp = jsonify({"status": "Required parameter function is missing"})
    resp.status_code = 404
    return resp

  try:
    value = request.json['value']
  except:
    value = None # No value is totally fine, some functions may not need one

  print(json.dumps(request.json, indent=4, ensure_ascii=False))

  path_for_device_binding = "devices/" + device + ".json"

  try:
    with open(path_for_device_binding) as device_binding_imported:
      device_binding = json.load(device_binding_imported)
  except:
    # No device file found
    resp = jsonify({"status": "Requested device not found"})
    resp.status_code = 404
    return resp

  # Forward to device binding
  for device_protocol_binding in device_binding['device']['protocols']:
    if protocol == device_protocol_binding:
      if protocol == "rest":
        return binding_rest.action(device_binding['device']['protocols'][protocol], function, value)
      elif protocol == "mqtt":
        return binding_mqtt.action(device_binding['device']['protocols'][protocol], function, value)
      elif protocol == "adb":
        return binding_adb.action(device_binding['device']['protocols'][protocol], function, value)

  # No protocol entry in device file matched with requested protocol
  resp = jsonify({"status": "Requested protocol not found in device file"})
  resp.status_code = 404
  return resp

app.run(host='0.0.0.0')
