from django.http import JsonResponse

from meiduo_mall.apps.users.models import User


def login_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            result = fn(request, *args, **kwargs)
            return result

        else:
            return JsonResponse({
                'code': 400,
                'errmsg': '用户未登录'
            })
    return wrapper