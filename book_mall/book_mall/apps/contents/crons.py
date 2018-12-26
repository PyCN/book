import time
from collections import OrderedDict

import os

from django.conf import settings
from django.template import loader

from contents.models import ContentCategory
from goods.models import GoodsChannel
from goods.utils import get_categories


def generate_static_index_html():
    """生成主页静态文件"""
    print('%s: generate_static_index_html' % time.ctime())
    # 定义有序字典变量: categories
    # 字典内容: 商品频道及分类菜单
    # 创建有序字典
    categories = get_categories()
    # categories = OrderedDict()
    # # 查询所有商品频道
    # channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # for channel in channels:
    #     # 获取频道所属的当前组
    #     group_id = channel.group_id
    #     if group_id not in categories:
    #         categories[group_id] = {'channels': [], 'sub_cats': []}
    #
    #     # 获取当前频道的类别
    #     # cat1为商品一级分类
    #     cat1 = channel.category
    #     # 往当前组内添加商品分类的信息
    #     categories[group_id]['channels'].append({
    #         'id': cat1.id,
    #         'name': cat1.name,
    #         'url': channel.url
    #     })
    #
    #     # cat2为商品二级分类对象
    #
    #     for cat2 in cat1.goodscategory_set.all():
    #         # 为cat2添加sub_cats属性
    #         cat2.sub_cats = []
    #         # cat3为商品三级分类对象
    #         for cat3 in cat2.goodscategory_set.all():
    #             cat2.sub_cats.append(cat3)
    #         categories[group_id]['sub_cats'].append(cat2)

    # 广告内容
    contents = {}
    # contents = {
    #     'index_lbt': [广告类型],
    #     'index_lbt': [广告类型],
    # }
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    # 渲染渲染
    context = {
        'categories': categories,
        'contents': contents
    }
    template = loader.get_template('index.html')
    html_text = template.render(context)

    # 主页静态文件存储路径
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)