#!/usr/bin/env python

"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_detail_html.py
"""
import sys

sys.path.insert(0, '../')

import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'book_mall.settings.develop'

import django

django.setup()

from django.template import loader
from django.conf import settings

from goods.utils import get_categories
from goods.models import SKU, Category


def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku id
    """
    # 商品分类菜单
    categories = get_categories()
    # 获取当前sku的信息
    sku = SKU.objects.get(id=sku_id)
    cat3 = sku.category
    cat2 = cat3.parent
    cat1 = cat2.parent
    cats = {
        'cat1': cat1,
        'cat2': cat2,
        'cat3': cat3,
    }
    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
        'sku': sku,
        'cats': cats
    }
    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/' + str(sku_id) + '.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

    print(sku_id)


if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generate_static_sku_detail_html(sku.id)
    # generate_static_sku_detail_html(1)
