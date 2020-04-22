import os
from flask import jsonify

def action(binding, function, value=None):
  # At this place, there usually is the standard validation (not special to binding): Valid function and value (if present)
  # However, this does only work when device file specifies function and values
  # binding_adb does uses device file only for target ip and port because adb uses standard functions and values which don't distinguish between devices
  target_ip = binding['ip']
  target_port = binding['port']
  target = target_ip + ":" + target_port

  # Connect function is the only one with only target as parameter
  if function == "connect":
    function_call = globals()[function]
    return function_call(target)
  else:
    try:
      function_call = globals()[function]
      return function_call(target, value)
    except:
      resp = jsonify({"status": "Requested function unknown"})
      resp.status_code = 404
      return resp

def send_text(target, value):
  connect(target)

  text_escaped = value.replace(' ','%s')
  command = "adb -s" + " " + target + " " + "shell input text" + " " + str('\"') + str(text_escaped) + str('\"')
  os.popen(command)

  resp = jsonify({"status": "ok"})
  resp.status_code = 200
  return resp

def send_keyevent(target, value):
  # Validate value against adb keyevent code list
  permitted_values = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84"]
  if not value in permitted_values:
    resp = jsonify({"status": "Value is invalid"})
    resp.status_code = 404
    return resp

  connect(target)

  command = "adb -s" + " " + target + " " + "shell input keyevent" + " " + value
  os.popen(command)

  resp = jsonify({"status": "ok"})
  resp.status_code = 200
  return resp

def connect(target):
  command = "adb connect" + " " + target
  os.popen(command)

  resp = jsonify({"status": "ok"})
  resp.status_code = 200
  return resp