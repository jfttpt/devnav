from django.urls import path
from . import views


app_name = 'wechat'

urlpatterns = [
    path('', views.weixin_main, name='weixin_main'),
    path('index', views.index, name='index'),
]
