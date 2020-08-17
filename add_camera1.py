import os
import django
os.environ.update({"DJANGO_SETTINGS_MODULE": "devnav.settings"})
django.setup()
from wechat.models import Device
from datetime import date
from dateutil import parser

timestamp = parser.isoparse("2020-08-17T00:00:00.000000Z"[:-1])
device_id = 'kf97a5a'
device_name = 'Camera-1'
device_ip = '192.168.128.22'
device_mac = '74:ee:2a:3b:d4:c6'
device_ssid = 'shanghai-cxc-cv'
device_ap_name = 'IHG-Room-1001'
device = Device(ts=timestamp.date(),device_id=device_id,device_name=device_name,device_ip=device_ip,device_mac=device_mac,device_ssid=device_ssid,device_ap_name=device_ap_name)
device.save()
