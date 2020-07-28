from django.shortcuts import render

# Create your views here.

# 定义类视图
from django.views import View

from users.models import User

from django.http import JsonResponse

import logging

logger = logging.getLogger('django')


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
