from django.db import models

# Create your models here.
from django.db import models

class Area(models.Model):
    name = models.CharField(max_length=20,
                            verbose_name='一级行政区名称')

    # 外键自关联字段 parent
    # 第一个参数是self，表示parent关联自己
    # on_delete=models.SET_NULL:如果省删掉了，省内其他信息为null
    # related_name='subs':设置以后，我们获取了省的对象
    # 替换django原始调用方法area.area_set.all()为area.subs.all()
    parent = models.ForeignKey('self',
                               on_delete=models.SET_NULL,
                               related_name='subs',
                               null=True,
                               blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name