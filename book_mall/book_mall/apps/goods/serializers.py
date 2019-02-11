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


class KeyWordSerializer(serializers.ModelSerializer):
    """图书关键字序列化器"""
    class Meta:
        model = models.KeyWord
        fields = ('id', 'name')