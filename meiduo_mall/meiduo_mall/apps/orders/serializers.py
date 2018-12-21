from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from carts.views import get_cart_dict, get_cart_str
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
import logging

from users.models import User

logger = logging.getLogger('django')


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    count = serializers.IntegerField(label='商品数量', min_value=1)

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """订单结算序列化器"""
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """保存订单序列化器"""

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        # read_only_fields = ('order_id')
        extra_kwargs = {
            'order_id': {
                'read_only': True
            },
            'address': {
                'write_only': True,
                'required': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """
        保存订单
        """
        # 获取当前下单用户
        user = self.context['request'].user
        # 获取常见订单数据
        # 组织订单编号 20170903153611+user.id
        # timezone.now() -> datetime
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + "%09d" % user.id
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 生成订单
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                # 创建订单信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0'),
                    freight=Decimal('10.0'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method==OrderInfo.PAY_METHODS_ENUM['CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )
                # 获取购物车信息
                redis_conn = get_redis_connection('cart')
                redis_cart_bytes = redis_conn.get('cart_%s' % user.id)
                if not redis_cart_bytes:
                    raise serializers.ValidationError('购物车没有数据')
                # 获取购物车字典
                cart_dict = get_cart_dict(redis_cart_bytes.decode())
                # 构建已勾选商品的字典
                cart = {}
                for sku_id, sku in cart_dict.items():
                    if sku['selected']:
                        cart[sku_id] = sku['count']
                if not cart:
                    raise serializers.ValidationError('购物车没有数据')
                # 处理订单商品
                for sku_id in cart.keys():
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        # 获取该商品的原始库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 获取当前用户购买的数量
                        sku_count = cart[sku.id]
                        if sku_count > origin_stock:
                            serializers.ValidationError('商品%s库存不足' % sku.name)

                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count

                        ret = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if ret == 0:
                            continue
                        # 累计商品的SPU 销量信息
                        sku.goods.sales += new_sales
                        # 保存SPU
                        sku.goods.save()
                        # 累计订单基本信息的数据
                        order.total_count += sku_count  # 累计当前订单商品数量
                        order.total_amount += sku_count * sku.price  # 累计当前订单商品总额
                        # 保存订单商品
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )
                        # 更新成功
                        break
                # 更新订单的金额数量信息
                order.total_amount += order.freight
                # 保存订单
                order.save()

            # 捕获序列化器异常
            except serializers.ValidationError:
                raise
            # 捕获全部异常
            except Exception as e:
                # 打印日志
                logger.warning(e)
                # 回到保存点
                transaction.savepoint_rollback(save_id)
                raise

            # 提交事务
            transaction.savepoint_commit(save_id)
            # 更新redis中保存的购物车数据
            for sku_id in cart:
                del cart_dict[sku_id]
            cart_str = get_cart_str(cart_dict)
            redis_conn.set('cart_%s' % user.id, cart_str)
            return order


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'default_image_url', 'name', 'caption', 'price')


class OrderGoodsSerializer(serializers.ModelSerializer):
    sku = SKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ('id', 'count', 'price', 'sku')


class OrderSerializer(serializers.ModelSerializer):
    """用于订单查询的序列化器"""
    skus = OrderGoodsSerializer(many=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'create_time', 'total_amount', 'pay_method', 'status', 'skus')


class UserSerializer(serializers.ModelSerializer):
    """下单用户"""
    class Meta:
        model = User
        fields = ('username', )


class OrderSerializer2(serializers.ModelSerializer):
    """通过当前订单查找下单的用户"""
    user = UserSerializer()

    class Meta:
        model = OrderInfo
        fields = ('user',)


class OrderGoodsCommentSerializer(serializers.ModelSerializer):
    sku_id = serializers.IntegerField(label='SKU编号', min_value=1)
    order = OrderSerializer2()

    class Meta:
        model = OrderGoods
        fields = ('sku_id', 'comment', 'order', 'is_anonymous', 'score')


class CommentSerializer(serializers.ModelSerializer):
    """商品评论序列化器"""
    id = serializers.IntegerField(label='购买商品编号', min_value=1)
    sku_id = serializers.IntegerField(label='商品编号', min_value=1)
    order_id = serializers.CharField(label='订单编号')

    class Meta:
        model = OrderGoods
        fields = ('id', 'order_id', 'sku_id', 'score', 'is_anonymous', 'comment')
        extra_kwargs = {
            'score': {
                'write_only': True,
                'required': True,
            },
            'is_anonymous': {
                'write_only': True,
                'required': True,
            },
            'comment': {
                'write_only': True,
                'required': True,
            },

        }



