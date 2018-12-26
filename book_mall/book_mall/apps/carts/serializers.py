from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """购物车数据序列化器"""
    sku_id = serializers.IntegerField(label='SKU编号', min_value=1)
    count = serializers.IntegerField(label='SKU数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate(self, attrs):
        sku_id = attrs['sku_id']
        # 商品是否存在校验
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            raise serializers.ValidationError('商品不存在')

        count = attrs['count']
        # 商品库存量是否满足
        if count > sku.stock:
            raise serializers.ValidationError('商品库存量不足')

        return attrs


class CartListSerializer(serializers.ModelSerializer):
    """购物车列表序列化器"""
    count = serializers.IntegerField(label='商品数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'selected', 'name', 'default_image_url', 'price')


class CartDeleteSerializer(serializers.Serializer):
    """购物车删除序列化器"""
    sku_id = serializers.IntegerField()

    def validate_sku_id(self, sku_id):
        try:
            SKU.objects.get(id=sku_id)
        except Exception as e:
            raise serializers.ValidationError('商品不存在')
        return sku_id


class CartSelectionSerializer(serializers.Serializer):
    """商品是否选定序列化器"""
    selected = serializers.BooleanField(label='是否选定')
