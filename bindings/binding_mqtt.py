#!/usr/bin/env python
# coding: utf8

import os
import paho.mqtt.client as mqtt
from flask import jsonify
from . import validation_standard
from dotenv import load_dotenv
load_dotenv()

def action(binding, function, value=None):
  # Do standard validation (not special to binding): Valid function and value (if present)
  # Remember, each binding has to implement its own validation on top of that for other things
  standard_request_validation = validation_standard.validate(binding, function, value)
  if not standard_request_validation.status_code == 200:
    return standard_request_validation
  
  broker_address=os.getenv("MQTT_BROKER_ADDRESS")
  client = mqtt.Client(client_id=os.getenv("MQTT_CLIENT"), clean_session=True)
  client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASSWORD"))
  client.connect(broker_address)

  topic = binding['topic']

  for command_description in binding['functions']:
    if command_description == function:
      subtopic = binding['functions'][function]['subtopic']
      payload_with_possible_placeholder = binding['functions'][function]['payload']
      
      if value == None:
        payload = payload_with_possible_placeholder
      else:
        payload = payload_with_possible_placeholder.replace('$VALUE$', value)

      client.publish(os.getenv("MQTT_ROOT_TOPIC") + "/" + topic + "/" + subtopic, payload, qos=1)
      client.disconnect()

      resp = jsonify({"status": "ok"})
      resp.status_code = 200
      return resp
