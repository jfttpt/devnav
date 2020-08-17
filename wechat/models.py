from django.db import models

# Create your models here.
class Device(models.Model):
    ts = models.DateField()
    device_id = models.CharField(max_length=30)
    device_name = models.CharField(max_length=30)
    device_ip = models.CharField(max_length=30)
    device_mac = models.CharField(max_length=30)
    device_ssid = models.CharField(max_length=30, null=True, blank=True)
    device_ap_name = models.CharField(max_length=30, null=True, blank=True)

