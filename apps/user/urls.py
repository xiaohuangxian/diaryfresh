# encoding:utf-8
__author__ = 'Fioman'
__time__ = '2019/2/23 15:07'

from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^register/', register, name='register'),
    # 激活邮件处理函数
    url(r'^active/(?P<token>.*)$', active_handle, name='active'),
    # 登录页面的视图函数
    url(r'^login/$', login_handle, name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    # 用户中心的视图类
    url(r'^$', UserView.as_view(), name='user'),
    # 用户中心-订单页
    url(r'^order/$', UserOrderView.as_view(), name='order'),
    # 用户中心-地址页
    url(r'^address/$', UserAddressView.as_view(), name='address'),
]
