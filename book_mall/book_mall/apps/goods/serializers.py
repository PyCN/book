from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from goods.search_indexes import SKUIndex
from . import models


class SKUSerializer(serializers.ModelSerializer):
    """SKU商品序列化器"""
    class Meta:
        model = models.SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments', 'sales')


class SKUIndexSerializer(HaystackSerializer):
    """SKU商品索引序列化器"""
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')


# class GoodsCategorySerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = models.GoodsCategory
#         fields = ('id', 'name')
#
#
# class GoodsChannelSerializer(serializers.ModelSerializer):
#     category = GoodsCategorySerializer()
#
#     class Meta:
#         model = models.GoodsChannel
#         fields = ('url', 'category')
#
#
# # class GoodsCategory2Serializer(serializers.ModelSerializer):
# #     sub_cats = GoodsCategorySerializer(many=True)
# #
# #     class Meta:
# #         model = models.GoodsCategory
# #         fields = ('sub_cats', 'name')
# #
# #
# # class GoodsCategoryListSerializer(serializers.ModelSerializer):
# #     channels = GoodsChannelSerializer(many=True)
# #     sub_cats = GoodsCategory2Serializer(many=True)
# #
# #     class Meta:
# #         model = models.GoodsChannel
# #         fields = ('channels', 'sub_cats')

