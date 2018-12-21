import base64
import pickle

from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from carts import constants
from goods.models import SKU
from . import serializers


def get_cart_dict(cart_str):
    """返回购物车字典"""
    cart_bytes = cart_str.encode()
    cart_base64 = base64.b64decode(cart_bytes)
    cart_dict = pickle.loads(cart_base64)
    return cart_dict


def get_cart_str(cart_dict):
    """购物车字符串"""
    cart_bytes = pickle.dumps(cart_dict)
    cart_base64 = base64.b64encode(cart_bytes)
    cart_str = cart_base64.decode()
    return cart_str


class CartView(GenericAPIView):
    """购物车"""

    def perform_authentication(self, request):
        """重写父类的用户验证方法，不在进入视图前就检查JWT"""
        pass

    def post(self, request):
        """增加购物车"""
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sku_id = data['sku_id']
        count = data['count']
        selected = data['selected']

        # 用户认证
        try:
            user = request.user
        except Exception:
            user = None
        # 判断用户是否登录
        redis_conn = get_redis_connection('cart')
        if user and user.is_authenticated:
            redis_cart_bytes = redis_conn.get('cart_%s' % user.id)
            cart_str = redis_cart_bytes.decode() if redis_cart_bytes else None
        else:
            cart_str = request.COOKIES.get('cart', None)

        cart_dict = {}
        if cart_str:
            cart_dict = get_cart_dict(cart_str)

        # 添加购物车
        # 判断当前SKU是否在购物车中
        if sku_id in cart_dict:
            # SKU存在购物车
            cart_dict[sku_id]['count'] += count
            cart_dict[sku_id]['selected'] = selected
        else:
            # SKU不在购物车
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

        cart_str = get_cart_str(cart_dict)
        response = Response(serializer.data)
        # 判断当前用户是否登录
        if user and user.is_authenticated:
            redis_conn.set('cart_%s' % user.id, cart_str)
        else:
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response

    def get(self, request):
        """显示购物车"""

        # 用户认证
        try:
            user = request.user
        except Exception:
            user = None

        # 判断用户是否登录
        cart_str = ""
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            cart_bytes = redis_conn.get('cart_%s' % user.id)
            if cart_bytes:
                cart_str = cart_bytes.decode()
        else:
            cart_str = request.COOKIES.get('cart', None)

        cart_dict = {}
        if cart_str:
            cart_dict = get_cart_dict(cart_str)
        sku_ids = cart_dict.keys()

        # 获取购物车中的所有商品
        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        serializer = serializers.CartListSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车数据"""
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        sku_id = data['sku_id']
        count = data['count']
        selected = data['selected']

        # 用户认证
        try:
            user = request.user
        except Exception:
            user = None

        # 判断用户是否登录
        redis_conn = get_redis_connection('cart')
        if user and user.is_authenticated:
            cart_bytes = redis_conn.get('cart_%s' % user.id)
            cart_str = cart_bytes.decode() if cart_bytes else None
        else:
            cart_str = request.COOKIES.get('cart', None)

        cart_dict = get_cart_dict(cart_str)

        if sku_id in cart_dict:
            cart_dict[sku_id]['count'] = count
            cart_dict[sku_id]['selected'] = selected

        cart_str = get_cart_str(cart_dict)
        response = Response(serializer.data)
        # 判断当前用户是否登录
        if user and user.is_authenticated:
            redis_conn.set('cart_%s' % user.id, cart_str)
        else:
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response

    def delete(self, request):
        """根据sku_id删除"""
        serializer = serializers.CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']

        # 用户认证
        try:
            user = request.user
        except Exception:
            user = None

        # 判断用户是否登录
        redis_conn = get_redis_connection('cart')
        if user and user.is_authenticated:
            redis_cart_bytes = redis_conn.get('cart_%s' % user.id)
            cart_str = redis_cart_bytes.decode() if redis_cart_bytes else None
        else:
            cart_str = request.COOKIES.get('cart', None)

        cart_dict = {}
        if cart_str:
            cart_dict = get_cart_dict(cart_str)
        if sku_id in cart_dict:
            del cart_dict[sku_id]

        cart_str = get_cart_str(cart_dict)
        response = Response({'message': 'OK'})
        # 判断当前用户是否登录
        if user and user.is_authenticated:
            redis_conn.set('cart_%s' % user.id, cart_str)
        else:
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response


class CartSelectionView(GenericAPIView):
    """购物车商品全选"""

    def perform_authentication(self, request):
        pass

    def put(self, request):
        serializer = serializers.CartSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data['selected']

        # 用户认证
        try:
            user = request.user
        except Exception:
            user = None

        # 判断用户是否登录
        redis_conn = get_redis_connection('cart')
        if user and user.is_authenticated:
            redis_cart_bytes = redis_conn.get('cart_%s' % user.id)
            cart_str = redis_cart_bytes.decode() if redis_cart_bytes else None
        else:
            cart_str = request.COOKIES.get('cart', None)

        cart_dict = {}
        if cart_str:
            cart_dict = get_cart_dict(cart_str)

        for sku_cart in cart_dict.values():
            sku_cart['selected'] = selected

        cart_str = get_cart_str(cart_dict)
        response = Response({'message': 'OK'})
        # 判断当前用户是否登录
        if user and user.is_authenticated:
            redis_conn.set('cart_%s' % user.id, cart_str)
        else:
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response







