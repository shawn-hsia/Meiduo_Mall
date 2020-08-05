import json
import re


from django.http import JsonResponse
from django.shortcuts import render
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
import logging
from django_redis import get_redis_connection
from django.contrib.auth import login
logger = logging.getLogger('django')
from oauth.models import OAuthQQUser
from django.views import View
from users.models import User

from oauth.utils import generate_access_token, check_access_token
# Create your views here.


class QQFirstView(View):
    def get(self, request):
        # 获取参数
        next_request = request.GET.get('next')

        # 校验参数
        # 处理数据

        # 获取qq登录页面
        # 创建OAuth类的对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next_request)
        # 调用对象获取qq登录跳转地址
        login_url = oauth.get_qq_url()

        # 构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'login_url': login_url
        })


#    qq登录第二个接口，判断用户的openid
class QQUserView(View):
    def get(self, request):
        # 接收参数
        code = request.GET.get('code')
        # 检验参数
        if not code:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少code参数'
            })
        # 处理数据
        # 创建oauth工具类，传入code，转化成access_code,再向qq服务器请求openid
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用oauth类对象的方法获取access_code
            access_token = oauth.get_access_token(code)
            # 使用oauth类对象的方法请求qq服务器获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': 'oauth2.0认证失败，获取用户qq认证消息失败'
            })

        try:
            # 如果存在openid，则获取oauth的外键对象，表明用户已经注册并绑定了qq
            # 状态保持
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
            user = oauth_qq.user
            login(request, user)
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok',
            })
            response.set_cookie('username',
                                user.username,
                                max_age=3600 * 24 * 14)
            return response
        except Exception as e:
            # 加密openid传给用户
            access_token = generate_access_token(openid)

            return JsonResponse({
                'access_token': access_token
            })

            # tb_oauth_qq里边没有openid
            # 有用户，没有绑定qq，绑定openid
            # 没有用户，也没有绑定openid
     # 有用户，也有openid，直接返回，状态保持
            # 利用oauth表的外键对象获取用户对象

        # 构建响应

    def post(self,request):
        # 获取参数
        dict = json.loads(request.body.decode())
        mobile = dict.get('mobile')
        password = dict.get('password')
        sms_code = dict.get('sms_code')
        access_code = dict.get('access_token')
        # 校验参数必要性
        if not all([mobile, password, sms_code, access_code]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必要参数'
            })
        # 验证每个参数是否符合格式要求
        # 手机号是否符合格式要求
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return JsonResponse({
                'code': 400,
                'errmsg': '手机号码格式不对'
            })
        # 判断密码是够符合格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return  JsonResponse({
                'code': 400,
                'errmsg': '密码格式不对'
            })
        # 判断验证码是否符合要求
        redis_conn = get_redis_connection('verify_code')
        sms_code_from_redis = redis_conn.get('sms_%s' % mobile)
        # 判断验证码是否已经过期
        if not sms_code_from_redis:
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码已经过期'
            })
        # 判断验证码是否正确
        if sms_code_from_redis.decode() != sms_code:
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码输入错误'
            })
        # 判断用户是否已经注册过

        # 解密获取用户的openid
        openid = check_access_token(access_code)
        try:
            user = User.objects.get(mobile=mobile)
            # 存在则继续校验用户密码是否输入正确
            if user.check_password(password):
                # 将oauth_qq表中的user外键绑定为user的id
                try:
                    OAuthQQUser.objects.create(user_id=user.id,
                                           openid=openid)
                    response = JsonResponse({
                        'code': 0,
                        'errmsg': 'ok'
                    })
                    #状态保持
                    login(request, user)
                    response.set_cookie('username', user.username,
                                        max_age=3600*24*14)
                    return response
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({
                        'code': 400,
                        'errmsg': '绑定用户信息失败，数据库写入错误'
                    })
            else:
                return JsonResponse({
                    'code': 400,
                    'errmsg': '密码输入错误',
                })
        # 用户没有注册过
        except Exception as e:
            # 在User模型类中创建用户信息
            try:
                user = User.objects.create_user(username=mobile,
                                                 password=password,
                                                 mobile=mobile)
                OAuthQQUser.objects.create(openid=openid,
                                           user_id=user.id)
                # 状态保持

                login(request, user)
                response = JsonResponse({
                    'code': 0,
                    'errmsg': 'ok',
                })
                response.set_cookie('username', user.username,
                                    max_age=3600*24*14)
                return response
            except Exception as e:
                logger.error(e)
                return JsonResponse({
                    'code': 400,
                    'errmsg': '用户数据保存失败，写入数据库出错'
                })


