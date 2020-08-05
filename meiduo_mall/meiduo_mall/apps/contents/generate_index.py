from django.template import loader
import os, sys
from django.conf import settings

from contents.models import ContentCategory, Content
from goods.models import GoodsChannel, GoodsCategory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

sys.path.insert(
    0,
    '/home/ubuntu/Desktop/项目阶段/meiduo_mall'
)

import django

django.setup()


def generate_static_index_html():
    # 模版参数categories是首页分类频道
    categories = {}

    # 获取首页所有的分类频道数据
    channels = GoodsChannel.objects.order_by(
        'group_id',
        'sequence'
    )
    # 遍历所有是分类频道，构建以组号作为key的键值对
    for channel in channels:
        # channel: GoodsChannel对象
        if channel.group_id not in categories:
            categories[channel.group_id] = {
                'channels': [],  # 当前分组中的分类频道(一级分类)
                'sub_cats': []  # 二级分类
            }
        # (1)、填充当前组中的一级分类
        cat1 = channel.category
        categories[channel.group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        # (2)、填充当前组中的二级分类
        cat2s = GoodsCategory.objects.filter(parent=cat1)
        for cat2 in cat2s:
            # cat2：二级分类对象

            cat3_list = []  # 每一次遍历到一个二级分类对象的时候，初始化一个空列表，用来构建三级分类
            cat3s = GoodsCategory.objects.filter(parent=cat2)
            # (3)、填充当前组中的三级分类
            for cat3 in cat3s:
                # cat3；三级分类对象
                cat3_list.append({
                    'id': cat3.id,
                    'name': cat3.name
                })

            categories[channel.group_id]['sub_cats'].append({
                'id': cat2.id,
                'name': cat2.name,
                'sub_cats': cat3_list  # 三级分类
            })

    # 模版参数contents是页面广告数据
    contents = {}
    # 广告分类(位置)
    content_cats = ContentCategory.objects.all()
    for content_cat in content_cats:
        # content_cat：是每一个广告的分类，如"轮播图"
        contents[content_cat.key] = Content.objects.filter(
            category=content_cat,
            status=True
        ).order_by('sequence')

    # 模版参数
    context = {
        'categories': categories,
        'contents': contents
    }

    # 页面渲染
    template = loader.get_template('index.html')
    # 渲染成文件
    html_content = template.render(context)
    # 写入到front_end_pc中替换原来的index.html
    index_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(index_path, 'w') as f:
        f.write(html_content)


def render_demo():
    # 该函数是用来测试django自动渲染的原理

    # 获取templates文件下的demo html文件
    template = loader.get_template('demo.html')
    # 构建数据填充内容
    contents = {
        "name": "shawn",
        "slogan": "python no.1",
    }
    # 渲染页面形成数据
    html_contents = template.render(contents)
    # 写入形成新的html页面
    with open('./demo.html', 'w') as f:
        f.write(html_contents)



if __name__ == '__main__':
    render_demo()