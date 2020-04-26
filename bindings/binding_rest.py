#!/usr/bin/env python
# coding: utf8

import json
from flask import jsonify
import requests
from . import validation_standard

def action(binding, function, value=None):
  # Do standard validation (not special to binding): Valid function and value (if present)
  # Remember, each binding has to implement its own validation on top of that for other things
  standard_request_validation = validation_standard.validate(binding, function, value)
  if not standard_request_validation.status_code == 200:
    return standard_request_validation

  target_address = binding['address']
  request_method = binding['request_method']

  for command_description in binding['functions']:
    if command_description == function:
      command_with_possible_placeholder = binding['functions'][function]['command']

      if value == None:
        command = command_with_possible_placeholder
      else:
        command = command_with_possible_placeholder.replace('$VALUE$', value)

      if request_method == "post":
        requests.post(target_address, data=command)
      else:
        resp = jsonify({"status": "server does not support request_method specified in device file"})
        resp.status_code = 500
        return resp
      
      resp = jsonify({"status": "ok"})
      resp.status_code = 200
      return resp

  # The program should not get here because the standard validation validates against correct function
  resp = jsonify({"status": "unknown server error"})
  resp.status_code = 500
  return resp