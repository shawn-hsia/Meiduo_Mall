from django.http import JsonResponse
from django.shortcuts import render
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings

from django.views import View
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

