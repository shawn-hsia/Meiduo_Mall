from django.shortcuts import render

# Create your views here.

# 定义类视图
from django.views import View
from django_redis import get_redis_connection



from django.http import JsonResponse

import logging

from users.models import User

logger = logging.getLogger('django')

import json

import re

from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from meiduo_mall.utils.view import login_required
# 判断用户注册时是否存在
class UsernameCountView(View):

    def get(self, request, username):

        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': 'error',
            })
        else:
            print(count)
            return JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'count': count

            })


# 验证注册时手机号是否存在
class MobileCountView(View):
    def get(self, request, mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception:
            return JsonResponse({
                'code': 400,
                'errmsg': 'error',

            })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count':count,
        })


# 用户注册接口
class RegisterView(View):
    # 接收参数
    def post(self, request):

      # 数据为请求体中的数据
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        sms_code = dict.get('sms_code')
        allow = dict.get('allow')


    # 校验参数
        if not all([username, password, password2, mobile, sms_code]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必要参数'
            })
        # 检验用户名是否符合规则
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg':'用户名格式不对'
            })
        # 检验用户密码是否格式正确
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({
                'code': 400,
                'errmsg': '用户名格式不对'
            })
        # 检验密码两次是否正确
        if password != password2:
            return JsonResponse({
                'code': 400,
                'errmsg': '两次输入密码不一致'
            })
        # 检验mobile格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'code': 400,
                'errmsg': '手机号码格式不对'
            })
        # 协议要求
        if allow == False:
            return JsonResponse({
                'code': 400,
                'errmsg': '请同意协议版本'
            })

        # 从redis从提取sms_code
        redis_conn = get_redis_connection('verify_code')
        sms_code_from_redis = redis_conn.get('sms_%s' % mobile)
        # 先判断该值是否存在
        if not sms_code_from_redis:
            return JsonResponse({
                'code': 400,
                'errmsg': '短信验证码已失效'
            })
        # 再判断用户输入的短信验证码是否正确
        if sms_code_from_redis.decode() != sms_code:
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码输入有误',
            })
    # 处理数据 ,保存到MySQL
        try:
            user = User.objects.create(username=username, mobile=mobile, password=password)
        except Exception as e:
            logger.error(e)
            print(e)
        else:
            user.save()
        # 实现用户保持，用户注册成功以后，在数据库中记录用户数据，并把用户数据状态返回给浏览器
        login(request, user) # 传入request和user对象，并把用户的信息存入session（redis缓存中）。再存入cookies返回给浏览器
    # 构建相应
        response =  JsonResponse({
            'code': 0,
            'errmsg': 'ok',
        })
        response.set_cookie(
            'username',
            username,
            max_age=3600*24*14
        )
        return response


#  处理用户登录的类视图函数
class LoginView(View):
    def post(self, request):
        # 接收参数， 为请求体携带数据
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        remembered = dict.get('remembered')
        # print(password)


        # 校验参数
        if not all([username, password]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必要参数'
            })
        # 校验用户名是否符合格式
        if not re.match(r'^\w{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg': '用户名格式有误'
            }
            )
        # 校验密码是否符合格式
        if not re.match(r'^\w{8,20}$',password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误'
            }
            )
        # 处理数据
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            try:
                user = User.objects.get(mobile=username)
            except User.DoesNotExist as e:
                logger.error(e)
                print(e)
                return JsonResponse({
                'code': 400,
                'errmsg': '用户名错误'
                })
        if user.password != password:
            return JsonResponse({
                'code':400,
                'errmsg': '密码错误',
            })

        # user = authenticate(request, username=username, password=password)
        # # 构建响应
        # if not user:
        #     return JsonResponse({
        #         'code': 400,
        #         'errmsg': '用户名或者密码有误'
        #     })

        # 状态保持
        login(request, user)
        # 判断用户是否勾选记住用户
        if remembered:
            # None表示默认14天，为用户保存14天
            request.session.set_expiry(None)
        else:
            # 0，表示关闭浏览器删除
            request.session.set_expiry(0)

       # 构建响应
        response = JsonResponse({
            'code': 0,
            'errmsg': "ok"
        })
        response.set_cookie(
            'username',
            username,
            max_age=3600*24*14
        )
        return response


# 用户退出接口
class LogoutView(View):
    # 定义请求方式
    def delete(self, request):
        # 清除session
        logout(request)
        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })
        # 清除用户的cookies
        response.delete_cookie('username')
        return response


# 用户中心页面接口

class UserInfoView(View):
    @method_decorator(login_required)
    def get(self, request):
        # 获取用户对象
        user = request.user
        # 构建用户响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'info_data': {
                'username': user.username,
                'mobile': user.mobile,
                'email': user.email,
                'email_active': user.email_active,
            }
        })