import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "devnav.settings"})
django.setup()
from wechat.models import Device
from datetime import date
from dateutil import parser
timestamp = parser.isoparse("2020-08-17T00:00:00.000000Z"[:-1])
device_id = 'k97ff52'
device_name = 'Camera-2'
device_ip = '192.168.128.23'
device_mac = '38:01:46:8c:74:b0'
device_ssid = 'shanghai-cxc-cv'
device_ap_name = 'Room-1001'
device = Device(ts=timestamp.date(),device_id=device_id,device_name=device_name,device_ip=device_ip,device_mac=device_mac,device_ssid=device_ssid,device_ap_name=device_ap_name)
device.save()
