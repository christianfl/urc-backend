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

  text = value.replace(' ','%s')
  text = text.replace('ä','ae')
  text = text.replace('ö','oe')
  text = text.replace('ü','ue')
  text = text.replace('ß','ss')

  # Send text to device
  try:
    response = device.shell('input text "' + text + '"')
  except:
    resp = jsonify({"status": "Could not send text to connected device"})
    resp.status_code = 500
    return resp

  resp = jsonify({"status": "Text sent to target"})
  resp.status_code = 200
  return resp

def send_keyevent(target_ip, target_port, target_adbkey, value):
  # Validate value against adb keyevent code list from https://developer.android.com/reference/android/view/KeyEvent.html
  permitted_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "113", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126", "127", "128", "129", "130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "140", "141", "142", "143", "144", "145", "146", "147", "148", "149", "150", "151", "152", "153", "154", "155", "156", "157", "158", "159", "160", "161", "162", "163", "164", "165", "166", "167", "168", "169", "170", "171", "172", "173", "174", "175", "176", "177", "178", "179", "180", "181", "182", "183", "184", "185", "186", "187", "188", "189", "190", "191", "192", "193", "194", "195", "196", "197", "198", "199", "200", "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "213", "214", "215", "216", "217", "218", "219", "220", "221", "222", "223", "224", "225", "226", "227", "228", "229", "230", "231", "232", "233", "234", "235", "236", "237", "238", "239", "240", "241", "242", "243", "244", "245", "246", "247", "248", "249", "250", "251", "252", "253", "254", "255", "256", "257", "258", "259", "260", "261", "262", "263", "264", "265", "266", "267", "268", "269", "270", "271", "272", "273", "274", "275", "276", "277", "278", "279", "280", "281", "282", "283", "284", "285", "286", "287", "288", "512", "1024", "4096", "8192", "16384", "28672", "65536", "131072", "262144", "458752", "1048576", "2097152", "4194304"]
  if not value in permitted_values:
    resp = jsonify({"status": "Value is invalid"})
    resp.status_code = 404
    return resp

  # Connect to device
  try:
    device = _connect(target_ip, target_port, target_adbkey)
  except:
    resp = jsonify({"status": "Could not connect to device"})
    resp.status_code = 500
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
  device.connect(rsa_keys=[signer], auth_timeout_s=1.)

  return device