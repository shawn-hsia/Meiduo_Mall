from django.contrib.auth.backends import ModelBackend

import re

from users.models import User


class UsernameMobileAuthBackend(ModelBackend):
    # 用户到底以何种方式登录
    # 重写authenticate方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            try:
                user = User.objects.get(mobile=username)
            except User.DoesNotExist as e:
                return None

        if user.check_password(password):
            return user
