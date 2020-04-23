import os
from subprocess import check_output
from flask import jsonify
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

def action(binding, function, value=None):
  # At this place, there usually is the standard validation (not special to binding): Valid function and value (if present)
  # However, this does only work when device file specifies function and values
  # binding_adb does uses device file only for target ip and port because adb uses standard functions and values which don't distinguish between devices
  target_ip = binding['ip']
  target_port = binding['port']
  target_adbkey = binding['adbkey_path']

  # _connect function is at the moment the only one which is not accessible from user by request
  # Naming convention is that the not accesible methods should begin with an underscore
  try:
    if function == "_connect":
      raise ValueError('Requested function not accessible.')
    function_call = globals()[function]
  except:
    resp = jsonify({"status": "Requested function unknown"})
    resp.status_code = 404
    return resp

  return function_call(target_ip, target_port, target_adbkey, value)

def send_text(target_ip, target_port, target_adbkey, value):
  # Connect to device
  try:
    device = _connect(target_ip, target_port, target_adbkey)
  except:
    resp = jsonify({"status": "Could not connect to device"})
    resp.status_code = 500
    return resp

  text_escaped = value.replace(' ','%s')

  # Send text to device
  try:
    response = device.shell('input text "' + text_escaped + '"')
  except:
    resp = jsonify({"status": "Could not send text to connected device"})
    resp.status_code = 500
    return resp

  resp = jsonify({"status": "Text sent to target"})
  resp.status_code = 200
  return resp

def send_keyevent(target_ip, target_port, target_adbkey, value):
  # Connect to device
  try:
    device = _connect(target_ip, target_port, target_adbkey)
  except:
    resp = jsonify({"status": "Could not connect to device"})
    resp.status_code = 500
    return resp

  # Validate value against adb keyevent code list from https://developer.android.com/reference/android/view/KeyEvent.html
  permitted_values = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85"]
  if not value in permitted_values:
    resp = jsonify({"status": "Value is invalid"})
    resp.status_code = 404
    return resp

  # Send key to device
  try:
    response = device.shell('input keyevent ' + value)
  except:
    resp = jsonify({"status": "Could not send text to connected device"})
    resp.status_code = 500
    return resp

  resp = jsonify({"status": "ok"})
  resp.status_code = 200
  return resp

# From here on only "private" methods which should not be directly accessible from user reuqest
# They usually don't return any HTTP conform return value
# Don't forget to include them in the if statement in def action(binding, function, value=None)

def _connect(target_ip, target_port, target_adbkey):
  # Open private key generated on first connect
  with open(target_adbkey) as f:
    priv = f.read()
  signer = PythonRSASigner('', priv)

  device = AdbDeviceTcp(target_ip, int(target_port), default_timeout_s=9.)
  device.connect(rsa_keys=[signer], auth_timeout_s=0.1)

  return device