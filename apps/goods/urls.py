# encoding:utf-8
from django.views.generic import TemplateView

__author__ = 'Fioman'
__time__ = '2019/2/23 15:07'

from django.conf.urls import url

urlpatterns = [
    url(r'^index/',TemplateView.as_view(template_name='index.html'),name='index')
]