import pymysql

pymysql.install_as_MySQLdb()

# 引入celery实例对象,这句话的作用是运行Django项目的时候,加载celery.py
from .celery import app as celery_app
