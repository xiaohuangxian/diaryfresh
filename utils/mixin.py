# encoding:utf-8
__author__ = 'Fioman'
__time__ = '2019/2/25 15:04'
from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as_view
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
