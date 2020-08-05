from django.shortcuts import render

# Create your views here.

# 定义类视图
from django.views import View
from django_redis import get_redis_connection

from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.email.tasks import send_verify_email
from django.http import JsonResponse

import logging

from users.models import User
from users.models import Address

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
            'count': count,
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
                'errmsg': '用户名格式不对'
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
            user = User.objects.create_user(username=username, mobile=mobile, password=password)
        except Exception as e:
            logger.error(e)
            print(e)
        else:
            user.save()
        # 实现用户保持，用户注册成功以后，在数据库中记录用户数据，并把用户数据状态返回给浏览器
        login(request, user)  # 传入request和user对象，并把用户的信息存入session（redis缓存中）。再存入cookies返回给浏览器
        # 构建相应
        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok',
        })
        response.set_cookie(
            'username',
            username,
            max_age=3600 * 24 * 14
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
        if not re.match(r'^\w{8,20}$', password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误'
            }
            )
        # 处理数据
        # try:
        #     user = User.objects.get(username=username)
        # except User.DoesNotExist as e:
        #     try:
        #         user = User.objects.get(mobile=username)
        #     except User.DoesNotExist as e:
        #         logger.error(e)
        #         print(e)
        #         return JsonResponse({
        #         'code': 400,
        #         'errmsg': '用户名错误'
        #         })
        # if user.password != password:
        #     return JsonResponse({
        #         'code':400,
        #         'errmsg': '密码错误',
        #     })

        user = authenticate(request, username=username, password=password)
        # 构建响应
        if not user:
            return JsonResponse({
                'code': 400,
                'errmsg': '用户名或者密码有误'
            })

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
            max_age=3600 * 24 * 14
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


#  添加邮箱后端接口
class EmailView(View):
    @method_decorator(login_required)
    def put(self, request):
        # 获取参数
        dict = json.loads(request.body.decode())
        email = dict.get('email')
        # 校验参数
        if not email:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少参数，用户未提交email地址'
            })
        if not re.match(r'^^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({
                'code': 400,
                'errmsg': '邮箱地址格式有误'
            })
        # 处理数据
        # 将获得的值存入MySQL数据库
        try:
            request.user.email = email
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '添加邮箱失败'
            })
        else:
            request.user.save()

        verify_url = request.user.generate_verify_email_url()
        # 构建邮件验证
        # 标题
        subject = "美多商城邮箱验证"
        # 发送内容:
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (request.user.email, verify_url, verify_url)

        # 进行发送
        send_verify_email.delay(subject=subject,
                                to_email=email,
                                html_message=html_message)
        # 构建返回
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok,邮箱添加成功'
        })


# 用户邮箱激活验证接口
class VerifyEmailView(View):
    def put(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少查询参数'
            })

        user = User.check_verify_email_token(token)
        if not user:
            return JsonResponse({
                "code": 400,
                'errmsg': '无效的token'
            })
        # 处理数据
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '激活邮件失败'
            })

        # 构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


# 用户新增地址接口
class CreateAddressView(View):
    def post(self, request):
        # 接收参数
        dict = json.loads(request.body.decode())
        receiver = dict.get('receiver')
        province_id = dict.get('province_id')
        city_id = dict.get('city_id')
        district_id = dict.get('district_id')
        place = dict.get('place')
        mobile = dict.get('mobile')
        tel = dict.get('tel')
        email = dict.get('email')
        # 校验参数，其中必传参数是；receiver，province_id,city_id,district_id
        # place,mobile
        if not all([receiver, province_id, city_id, district_id,
                    place, mobile]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必传参数',
            })
        # 一个用户只能最多拥有20个收货地址
        count = Address.objects.filter(user=request.user,
                                       is_deleted=False).count()
        if count > 20:
            return JsonResponse({
                'code': 400,
                'errmsg': '登录用户收货地址超过20个'
            })
        # 检验用户输入的收货地址中的手机号格式
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '参数mobile有误'})
        # 如果用户输入了tel和email，则校验用户输入的tel和email格式
        if tel:
            if not re.match(r'^1[3-9]\d{9}$', mobile):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数mobile有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数email有误'})
        # 处理数据，存入数据库中
        try:
            address = Address.objects.create(user=request.user,
                                             title=receiver,
                                             receiver=receiver,
                                             province_id=province_id,
                                             city_id=city_id,
                                             district_id=district_id,
                                             place=place,
                                             mobile=mobile,
                                             tel=tel,
                                             email=email)
            address_dict = {'id': address.id,
                            'title': address.title,
                            'receiver': address.receiver,
                            'province': address.province.name,
                            'city': address.city.name,
                            'district': address.district.name,
                            'place': address.place,
                            'mobile': address.mobile,
                            'tel': address.tel,
                            'email': address.email}

            # 设置用户的默认地址
            if not request.user.default_address:
                try:
                    request.user.default_address = address
                    request.user.save()
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({
                        'code': 400,
                        'errmsg': '设置用户默认地址失败'
                    })
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '创建用户收货地址失败'
            })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': address_dict
        })


# 展示当前用户的所有收货地址
class AddressView(View):
    def get(self, request):
        # Address模型类的外键user的所有地址返回
        try:
            addresses = Address.objects.filter(user=request.user,
                                               is_deleted=False)
            address_list = []
            # 遍历所有地址集，获取每一个地址的相关属性返回
            for address in addresses:
                address_dict = {
                    'id': address.id,
                    'title': address.title,
                    'receiver': address.receiver,
                    'province': address.province.name,
                    'city': address.city.name,
                    'mobile': address.mobile,
                    'district': address.district.name,
                    'place': address.place,
                    'tel': address.tel,
                    'email': address.email,
                }
                # 将默认地址移动到列表最前
                default_address = request.user.default_address
                if default_address.id == address.id:
                    address_list.insert(0, address_dict)
                else:
                    address_list.append(address_dict)
            # 获取默认地址

            # 构建响应返回
            default_address_id = request.user.default_address_id
            return JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'addresses': address_list,
                'default_address_id': default_address_id

            })
        except Exception as e:
            logger.info(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '已登录用户没有创建任何收货地址'
            })


# 当前登录用户修改收货地址视图函数
class UpdateDestroyAddressView(View):
    # 修改地址提交方法
    def put(self, request, address_id):
        # 接收参数
        dict = json.loads(request.body.decode())
        receiver = dict.get('receiver')
        province_id = dict.get('province_id')
        city_id = dict.get('city_id')
        district_id = dict.get('district_id')
        place = dict.get('place')
        mobile = dict.get('mobile')
        tel = dict.get('tel')
        email = dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place,
                    mobile]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必要参数'})
        # 校验如果有则校验固定电话
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数tel有误'})
        # 如果存在则校验email格式是否正确
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数email有误'})
        # 修改对应的地址
        try:
            Address.objects.filter(id=address_id).update(
                user = request.user,
                title = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '写入数据库失败'
            })
        address = Address.objects.get(id = address_id)
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email

        }
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': address_dict
        })

    # 删除地址
    def delete(self, request, address_id):
        # 接收参数
        if not address_id:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必传参数'
            })
        try:
            address = Address.objects.get(id= address_id)
            # 逻辑删除
            address.is_deleted= True
            address.save()
            return JsonResponse({
                'code': 0,
                'errmsg': 'ok'
            })
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '删除用户地址失败'
            })


# 修改默认地址类视图
class DefaultAddressView(View):
    def put(self, request, address_id):
        if not address_id:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必要参数'
            })
        try:
            request.user.default_address_id = address_id
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '修改用户默认收货地址失败'
            })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


# 修改用户收货地址的标题
class UpdateTitleAddressView(View):
    def put(self, request, address_id):
        dict = json.loads(request.body.decode())
        title = dict.get('title')
        if not all([address_id, title]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必传参数'
            })
        try:
            address = Address.objects.get(id= address_id)
            address.title = title
            return JsonResponse({
                'code': 0,
                'errmsg': 'ok'
            })
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '设置地址标题失败'
            })


# 修改用户密码
class ChangePasswordView(View):
    def put(self,request):
        # 接收参数
        dict = json.loads(request.body.decode())
        old_password = dict.get('old_password')
        new_password = dict.get('new_password')
        new_password2 = dict.get('new_password2')
        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必传参数'
            })
        result = request.user.check_password(old_password)
        if not result:
            return JsonResponse({
                'code': 400,
                'errmsg': '原始密码有误'
            })
        # 判断新密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code':400,
                                 'errmsg':'密码格式不对，密码最少8位,最长20位'})
        # 判断两次密码是否一致
        if new_password != new_password2:
            return JsonResponse({
                'code': 400,
                'errmsg': '两次密码输入不一致'
            })
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '修改密码失败'
            })
        # 状态清除
        logout(request)
        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })
        response.delete_cookie('username')
        return response



