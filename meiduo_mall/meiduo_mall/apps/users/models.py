from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings


# 类继承方法
from meiduo_mall.utils.BaseModel import BaseModel


class User(AbstractUser):
    # 增加mobile字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 增加email_active 字段，默认为False未激活
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # 增加用户默认收货地址的字段，关联address对象
    default_address = models.ForeignKey('Address',
                                        related_name='users',
                                        null=True,
                                        blank=True,
                                        on_delete=models.SET_NULL,
                                        verbose_name='默认收货地址')

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


# 定义用户保存收货地址的模型类
class Address(BaseModel):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name='用户')
    province = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='province_addresses',
                                 verbose_name='省')
    city = models.ForeignKey('areas.Area',
                             on_delete=models.PROTECT,
                             related_name='city_addresses',
                             verbose_name='市')
    district = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='district_addresses',
                                 verbose_name='区')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20,verbose_name='收件人姓名')
    place = models.CharField(max_length=50, verbose_name='详细收货信息')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20,
                           null=True,
                           blank=True,
                           default='',
                           verbose_name='固定电话')
    email = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False,
                                     verbose_name="逻辑删除")
    class Meta:
        db_table = 'tb_addresses'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']









