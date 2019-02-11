import time
from collections import OrderedDict

import os

from django.conf import settings
from django.template import loader

from contents.models import ContentCategory
from goods.utils import get_categories
from goods.models import Advertise, AdvertiseCategory, SKU


def generate_static_index_html():
    """生成主页静态文件"""
    print('%s: generate_static_index_html' % time.ctime())
    # 定义有序字典变量: categories
    # 字典内容: 商品频道及分类菜单
    # 创建有序字典
    categories = get_categories()
    # 广告内容
    contents = {}
    # contents = {
    #     'index_lbt': [广告类型],
    #     'index_lbt': [广告类型],
    # }
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 图书广告
    advertise_categories = AdvertiseCategory.objects.all()
    advertises = []
    for cat in advertise_categories:
        advertise = {}
        advertise['cat'] = cat
        advertise['skus_cats'] = []
        advertise['skus'] = []
        for a in Advertise.objects.filter(category=cat):
            # advertise['skus'].append(a.sku)
            if a.sku.category not in advertise['skus_cats']:
                advertise['skus_cats'].append(a.sku.category)

        for cat in advertise['skus_cats']:
            advertise['skus'].append(SKU.objects.filter(category=cat, advertise__category=advertise['cat']))

        advertises.append(advertise)

    # 渲染渲染
    context = {
        'categories': categories,
        'contents': contents,
        'advertises':advertises
    }
    template = loader.get_template('index.html')
    html_text = template.render(context)

    # 主页静态文件存储路径
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)