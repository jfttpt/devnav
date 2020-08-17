import os
import django

os.environ.update({"DJANGO_SETTINGS_MODULE": "devnav.settings"})
django.setup()

from wechat.models import Device

Device.objects.all().delete()
