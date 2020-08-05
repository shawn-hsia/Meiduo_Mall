from django.shortcuts import render
from django.views import View
# Create your views here.
from areas.models import Area
from django.http import JsonResponse
import logging
logger = logging.getLogger('django')
from django.core.cache import cache



# 第一级行政区划接口
class ProvinceAreasView(View):
    def get(self, request):
        # 判断是否有缓存
        province_list = cache.get('province_list')
        if not province_list:
            try:
                province_data = Area.objects.filter(parent__isnull=True)
                province_list = []
                for province in province_data:
                    province_list.append({
                        'id': province.id,
                        'name': province.name
                    })
                # 写入缓存
                cache.set('province_list', province_list, 3600)
                return JsonResponse({
                    'code': 0,
                    'errmsg': 'ok',
                    'province_list': province_list,
                })
            except Exception as e:
                logger.error(e)
                return JsonResponse({
                    'code': 400,
                    'errmsg': '获取数据库数据失败',
                })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'province_list': province_list,})


# 子行政区接口
class SubAreasView(View):
    def get(self, request, pk):
        # 接收参数
        if not pk:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少参数'
            })
        # 检验参数
        # 提取父级对象
        # 读取缓存
        subs_data = cache.get("subs_data" + pk)
        if not subs_data:
            try:
                parent = Area.objects.get(id=pk)
                # 查询所有符合的子集
                subs = Area.objects.filter(parent_id=pk)
                subs_list = []
                for sub in subs:
                    subs_list.append({
                        'id': sub.id,
                        'name': sub.name,
                    })
                subs_data = {
                    'id': parent.id,
                    'name': parent.name,
                    'subs': subs_list

                }
                # 创建缓存
                cache.set('subs_data' + pk, subs_data, 3600)
                return JsonResponse({
                    'code': 0,
                    'errmsg': 'ok',
                    'sub_data': subs_data
                })
            except Exception as e:
                logger.error(e)
                return JsonResponse({
                    'code': 400,
                    'errmsg': '获取数据库数据失败'
                })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'sub_data': subs_data
        })
        # 处理数据
        # 构建ex响应
