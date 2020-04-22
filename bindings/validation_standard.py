import json
from flask import jsonify

def validate(binding, function, value=None):
  for command_description in binding['functions']:
    if command_description == function:
      # Check if parameter value is valid (see device file.json)
      is_value_valid = False

      # If function doesn't need a value, no value is also ok
      if value == None and binding['functions'][function]['values'] == []:
        is_value_valid = True

      # All values are permitted if device file states values = "permit_all"
      elif binding['functions'][function]['values'] == "permit_all":
        is_value_valid = True

      # Look up in device file wether value is valid
      else:
        for possible_value in binding['functions'][function]['values']:
          if value == possible_value:
            is_value_valid = True
            break

      if not is_value_valid and value == None:
        resp = jsonify({"status": "Value is required for requested function but you didn't send any"})
        resp.status_code = 404
        return resp

      if not is_value_valid:
        resp = jsonify({"status": "Value is invalid"})
        resp.status_code = 404
        return resp

      resp = jsonify({"status": "ok"})
      resp.status_code = 200
      return resp

  # If the requested function existed, the method would have already returned status: ok
  resp = jsonify({"status": "Requested function unknown"})
  resp.status_code = 404

  return resp