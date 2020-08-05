from django.db import models
from meiduo_mall.utils.BaseModel import BaseModel


# Create your models here.

#  定义qq登录的模型类
class OAuthQQUser(BaseModel):
    # QQ登录用户数据

    # user字段是个外键，默认绑定User模型类的id
    user = models.ForeignKey('users.User',
                             on_delete=models.CASCADE,
                             verbose_name='用户')

    # qq颁发的用户身份id
    openid = models.CharField(max_length=64,
                              verbose_name='openid',
                              db_index=True)
    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'qq登录用户数据'
        verbose_name_plural = verbose_name