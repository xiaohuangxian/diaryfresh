# encoding:utf-8
__author__ = 'Fioman'
__time__ = '2019/2/23 14:30'

from django.db import models

class BaseModel(models.Model):
    ''' 抽象模型基类,所有的模型都继承这个类 '''
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        # 说明是一个抽象类
        abstract = True