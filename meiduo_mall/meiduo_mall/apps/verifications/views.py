import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection

from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from meiduo_mall.libs.captcha.captcha import captcha
import logging
logger = logging.getLogger('django')


# Create your views here.
from django.views import View

# 处理前端在加载register页面对验证码的请求
class ImageCodeView(View):
    def get(self, request, uuid):
        # 使用captcha包获取验证码图片和图片中的文字
        text, image = captcha.generate_captcha()
        # 使用django包操作redis数据库存入text，key为uuid
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, 300, text)  # 有效时间是300s,写入前端 传入的uuid字段为key，生成的text为value
        return HttpResponse(image, content_type='image/jpg')


# 处理短信验证的请求
class SMSCodeView(View):
    def get(self, request, mobile):
        # 接收参数
        # 获取客户端请求发来的验证码，和对应的uuid
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 校验参数是否存在
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400,
                                 'errmsg':"缺少必要传输参数"})


        # 判断是否间隔60S在提交数据
        redis_conn = get_redis_connection('verify_code')
        flag = redis_conn.get("flag_%s" % mobile)
        if flag:
            return JsonResponse({
                'code': 400,
                'errmsg': 'please wait 60s',
            }, status=400)

        # 创建redis对象获取redis中存入的text
        text_from_redis = redis_conn.get("img_%s" % uuid)
        # 判断提取的验证码是否存在
        if not text_from_redis:
            return JsonResponse({
                'code':400,
                'errmsg':"image_code is out of use"
            },status=400)

        # 读取成功了以后就删除这个验证码
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)

        # 判断提取的验证码是否等于用户输入的验证码
        if text_from_redis.decode().lower() != image_code.lower():
            return JsonResponse({
                'code': 400,
                'errmsg': 'image not match'
            }, status=400)

        # 生成6位随机验证码
        sms_code = "%06d" % random.randint(0,999999)
        logger.info(sms_code)  # 记录日志。

        # #防止用户一直请求发送验证码
        # redis_conn.setex("flag_%s" % mobile, 60, 1)
        #
        #
        # redis_conn.setex('sms_%s' % mobile,
        #                  300,
        #                  sms_code)

        # pipeline
        p1 = redis_conn.pipeline()
        p1.setex("flag_%s" % mobile, 60, 1)
        p1.setex('sms_%s' % mobile,
                         300,
                         sms_code)
        p1.execute()

        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # print(sms_code)

        # Celery写法。
        from celery_tasks.sms.tasks import ccp_sms_code
        ccp_sms_code.delay(mobile, sms_code)

        return JsonResponse({
            'code':0,
            'errmsg':'验证短信发送成功',
        })



