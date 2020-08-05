from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from goods.models import GoodsCategory, SKU
import logging
logger = logging.getLogger('django')
from goods.utils import get_breadcrumb
from django.core.paginator import Paginator, EmptyPage

# Create your views here.
class ListView(View):
    def get(self, request, category_id):
        # 获取参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')
        # 校验参数
        if not all([page, category_id, page, page_size]):
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必传参数'
            })
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '获取商品分类数据出错'
            })
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)
        # 获取三级分类category的sku具体商品，并按照传入的方式排序
        try:
            skus = SKU.objects.filter(category=category).order_by(ordering)
        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '获取具体商品sku失败'
            })
        # 使用分页器获取分页的所有对象的商品
        paginator = Paginator(skus, page_size)
        try:
            # 获得用户指定页的skus对象，
            page_skus = paginator.page(page)
        except EmptyPage as e:
            return JsonResponse({
                'code': 400,
                'errmsg': '分页超出产品数'
            })
        # 获取用户指定的category对应商品总页数
        total_page = paginator.num_pages
        # 遍历用户指定的页码商品sku构建响应返回
        list =[]
        for sku in page_skus:
            list.append({
                'id': sku.id,
                'default_image_url': sku.default_image_url.url,
                'name': sku.name,
                'price': sku.price
            })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'list': list,
            'count': total_page,
            'breadcrumb': breadcrumb
        })


# 热销商品函数类视图函数
class HotGoodsView(View):
    def get(self,request, category_id):
        if not category_id:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少必传参数'
            })
        # 根据sku外键category获取sku销量倒叙获取对象返回

        # 按照销量倒叙排序取前两个
        try:
            skus = SKU.objects.filter(category_id=category_id,
                                 is_launched=True).order_by('-sales')[:2]
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'errmsg': '获取热销商品失败'
            })
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image_url.url,
                'name': sku.name,
                'price': sku.price
            })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'hot_skus': hot_skus
        })



