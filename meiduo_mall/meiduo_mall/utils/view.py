from django.http import JsonResponse

# from meiduo_mall.apps.users.models import User
# :
# 原因是装饰器会在工程运行之处加载装饰，此时此刻工程还未初始化完毕
# :
# 相关应用还未完全加载
# :
# 此刻导入app会发生不可未知错误

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