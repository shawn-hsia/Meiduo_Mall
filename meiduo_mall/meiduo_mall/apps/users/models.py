from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings


# 类继承方法
class User(AbstractUser):
    # 增加mobile字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 增加email_active 字段，默认为False未激活
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')


    # 对当前表进行相关设置
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    # 定义生成验证链接方法
    def generate_verify_email_url(self):
        # 序列器生成参数，有效期一天
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                    expires_in=3600*24)
        # 拼接参数
        data = {'user_id':self.id, 'email': self.email}
        # 加密生成token值，这个值是byte类型
        token = serializer.dumps(data).decode()
        # 拼接url
        verify_url = settings.EMAIL_VERIFY_URL + token

        return verify_url

    # 验证用户信息提取信息
    @staticmethod
    def check_verify_email_token(token):
        # 提取参数
        # 调用itsdangerous类生成serializer对象
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                     expires_in=3600*24)
        try:
            data = serializer.loads(token)
        except BadData:
            # 如果没有获取值，则报错
            return None
        else:
            user_id = data.get('user_id')
            email = data.get('email')

        # 校验参数
        try:
            user = User.objects.get(id=user_id, email= email)
        except Exception as e:
            return None
        else:
            # 查询到对应用户数据则返回用户对象
            return user










