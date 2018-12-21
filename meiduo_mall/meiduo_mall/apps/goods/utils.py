from collections import OrderedDict
from .models import GoodsChannel


def get_categories():
    """
    获取商城商品分类菜单
    :return 菜单字典
    """
    # categories = OrderedDict()
    # channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # for channel in channels:
    #     group_id = channel.group_id  # 当前组
    #
    #     if group_id not in categories:
    #         categories[group_id] = {'channels': [], 'sub_cats': []}
    #
    #     cat1 = channel.category  # 当前频道的类别
    #
    #     # 追加当前频道
    #     categories[group_id]['channels'].append({
    #         'id': cat1.id,
    #         'name': cat1.name,
    #         'url': channel.url
    #     })
    #     # 构建当前类别的子类别
    #     for cat2 in cat1.goodscategory_set.all():
    #         cat2.sub_cats = []
    #         for cat3 in cat2.goodscategory_set.all():
    #             cat2.sub_cats.append(cat3)
    #         categories[group_id]['sub_cats'].append(cat2)
    # return categoriescategories = OrderedDict()
    # channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # for channel in channels:
    #     group_id = channel.group_id  # 当前组
    #
    #     if group_id not in categories:
    #         categories[group_id] = {'channels': [], 'sub_cats': []}
    #
    #     cat1 = channel.category  # 当前频道的类别
    #
    #     # 追加当前频道
    #     categories[group_id]['channels'].append({
    #         'id': cat1.id,
    #         'name': cat1.name,
    #         'url': channel.url
    #     })
    #     # 构建当前类别的子类别
    #     for cat2 in cat1.goodscategory_set.all():
    #         cat2.sub_cats = []
    #         for cat3 in cat2.goodscategory_set.all():
    #             cat2.sub_cats.append(cat3)
    #         categories[group_id]['sub_cats'].append(cat2)
    # return categories
    categories = OrderedDict()
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id  # 当前组

        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别
        for cat2 in cat1.goodscategory_set.all():
            sub_cats = {'name': "", 'sub_cats': []}
            sub_cats['name'] = cat2.name
            for cat3 in cat2.goodscategory_set.all():
                sub_cats['sub_cats'].append({
                    'id': cat3.id,
                    'name': cat3.name,
                })
            categories[group_id]['sub_cats'].append(sub_cats)
    return categories
