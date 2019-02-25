from django.shortcuts import render, redirect, HttpResponse
import re
from django.core.mail import send_mail
from django.views.generic.base import View

from .models import User
from django.core.urlresolvers import reverse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from diaryfresh import settings
from celery_task import task
from django.contrib.auth import authenticate, login, logout
from utils.mixin import *


# 注册用的视图函数
def register(request):
    if request.method == 'POST':
        # 1. 首先是获取页面上提交过来的数据
        username = request.POST.get('user_name', None)
        password = request.POST.get('pwd', None)
        email = request.POST.get('email', None)
        allow = request.POST.get('allow', None)

        # 2. 进行数据校验
        # 2.1 校验完整性,使用all
        if not all([username, password, email, allow]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 2.2 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不对'})
        # 2.3 协议是否打钩,也就是后端如何获取checkbox是否被勾选,使用on来判断
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '必须同意协议'})

        # 3.验证用户名是否重合
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        # 如果用户名存在
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已经存在'})

        # 4.注册业务逻辑的实现,使用user的create_user()方法
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  # 注册的时候默认不激活,也可以在数据库模型中设置默认值为false
        user.save()

        # 5. 用户激活业务逻辑实现
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 创建加密对象(其中3600代表生效时间)
        # 创建一个字典,用来存放我们的用户信息,然后将这个字典加密
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        # 转换为字符串
        token = str(token, encoding='utf-8')

        # 发送激活邮件
        receiver = [email, ]

        # 异步的发送邮件任务
        task.send_register_active_email(receiver, username, token)

        # 返回应答,跳转到首页,使用反向解析的方法   /index/
        return redirect(reverse('goods:index'))  # 其实就是namespace为goods,别名为index的url

    return render(request, 'register.html')


# 处理用户激活的视图函数
def active_handle(request, token):
    # 进行解密,首先是获取工具对象
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        info = serializer.loads(token)
        # 获取待激活用户的id
        user_id = info['confirm']

        # 如果没有出现异常,则获取用户信息,并设置为激活状态
        user = User.objects.get(id=user_id)
        user.is_active = 1
        user.save()

        return redirect(reverse('user:login'))
    except SignatureExpired as e:
        # 激活链接已经过期
        return HttpResponse("激活链接已经过期!")


# 登录视图处理函数
def login_handle(request):
    if request.method == 'POST':
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 用户已经激活
                # 记录用户的登录状态, 使用login函数,可以将登录状态保存到session中,使用redis.
                login(request, user)

                # 登录有可能是从其他页面转过来的,这时候登录成功后需要跳转到之前用户访问的页面
                next_url = request.GET.get('next', reverse('goods:index'))  # 如果不是从其他页面跳转过来就默认是首页

                # 判断是否记住了密码,然后在response对象里设置cookie
                response = redirect(next_url)
                # 判断是否记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
                    # 返回response对象
                return response

            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

    # 返回应答
    # 首先判断是否记住用户名
    if 'username' in request.COOKIES:
        username = request.COOKIES.get('username')
        checked = 'checked'
    else:
        username = ''
        checked = ''

    return render(request, 'login.html', {'username': username, 'checked': checked})


# 登出注销的视图类
class LogoutView(View):
    def get(self, request):
        # 使用logout模块,自动回注销session
        logout(request)
        return redirect(reverse('goods:index'))


# 用户中心的视图类
class UserView(LoginRequiredMixin, View):
    # page 是用告诉前端页面显示的是哪个页面.
    def get(self, request):
        return render(request, 'user_center_info.html', {'page': 'user'})


# 用户中心订单视图类
class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_order.html', {'page': 'order'})


# 用户中心用户地址视图类
class UserAddressView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_site.html', {'page': 'address'})
