"""
自定义存储后端，使得文件的请求能正确到达storage的data
"""

from django.core.files.storage import Storage
from django.conf import settings

class FastDFSStorage(Storage):
    def open(self, name, mode='rb'):
        return None

    def save(self, name, content, max_length=None):
        pass

    def url(self, name):
        # 使用该函数重写ImageFiled.url的地址
        # name表示存储在data上的值
        # 返回的值为约定的服务器地址端口和data的值
        return settings.FDFS_URL + name