# -*- coding: utf-8 -*-
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wechatpy import parse_message, create_reply
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.pay import logger
from wechatpy.replies import TextReply
from wechatpy.utils import check_signature
from . import models
from wechat import utils

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from datetime import date
from dateutil import parser
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

print("start a scheduler")
# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')

# 每天0点半执行这个任务
@register_job(scheduler, 'cron', id=None, hour=0, minute=30)
def find_camera():
    # 具体要执行的代码
    print("execute find camera job")
    cameras = utils.find_camera_from_meraki()
    models.Device.objects.all().delete()
    if len(cameras) != 0:
        for camera in cameras:
            if camera.ssid is None:
                continue
            else:
                ts = parser.isoparse(camera.ts[:-1])
                device_id = camera.device_id
                device_name = camera.device_name
                device_ip = camera.device_ip
                device_mac = camera.device_mac
                device_ssid = camera.ssid
                device_ap_name = camera.ap_name
                device = models.Device(ts=ts.date(),device_id=device_id,device_name=device_name,device_ip=device_ip,device_mac=device_mac,device_ssid=device_ssid,device_ap_name=device_ap_name)
                device.save()

# 注册定时任务并开始
register_events(scheduler)
scheduler.start()

token = 'ciscoGuanYu123456'

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

#django默认开启csrf防护，这里使用@csrf_exempt去掉防护
@csrf_exempt
def weixin_main(request):
    # GET 方式用于微信公众平台绑定验证
    if request.method == 'GET':
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echo_str = request.GET.get('echostr', '')
        try:
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException:
            echo_str = '错误的请求'
        response = HttpResponse(echo_str)
        return response

    elif request.method == 'POST':
        msg = parse_message(request.body)
        if msg.type == 'text':
            if msg.content == 'camera?':
                cameras = models.Device.objects.all()
                text = "今天发现{count}个隐藏摄像头".format(count=len(cameras))
                if len(cameras) == 0:
                    text = text + '\n'
                else:
                    text = text + ',请管理员尽快处理\n'
                for camera in cameras:
                    text = text + '关联AP名称:' + str(camera.device_ap_name) + ';'
                    text = text + ' 设备MAC:' + str(camera.device_mac) + ';'
                    text = text + ' 设备IP:' + str(camera.device_ip) + '\n'
                reply = create_reply(text, msg)
            else:
                reply = create_reply('我不知道你要查询的设备信息，目前只支持查询隐藏摄像头，如果你要查询隐藏摄像头，请输入camera?', msg)
        elif msg.type == 'image':
            reply = create_reply('这是条图片消息', msg)
        elif msg.type == 'voice':
            reply = create_reply('这是条语音消息', msg)
        else:
            reply = create_reply('这是条其他类型消息', msg)
        response = HttpResponse(reply.render(), content_type="application/xml")
        return response
