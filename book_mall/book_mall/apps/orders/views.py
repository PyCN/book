from decimal import Decimal
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.views import get_cart_dict
from goods.models import SKU
from orders.models import OrderGoods, OrderInfo

from . import serializers
import logging
logger = logging.getLogger('django')


class OrderSettlementView(APIView):
    """订单结算"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 从redis中获取已勾选的商品信息
        user = request.user
        redis_conn = get_redis_connection('cart')
        cart_bytes = redis_conn.get('cart_%s' % user.id)
        # 遍历数据
        if not cart_bytes:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        cart_dict = get_cart_dict(cart_bytes.decode())
        # 构建已勾选商品的字典
        cart = {}
        for sku_id, sku in cart_dict.items():
            if sku['selected']:
                cart[sku_id] = sku['count']

        # 查询所有的商品数据
        sku_obj_list = SKU.objects.filter(id__in=cart.keys())

        # 遍历sku_obj_list
        for sku in sku_obj_list:
            sku.count = cart[sku.id]
        # 商品运费不具体实现
        freight = Decimal('10.00')
        serializer = serializers.OrderSettlementSerializer({'freight': freight, 'skus': sku_obj_list})
        return Response(serializer.data)


class OrderView(CreateAPIView):
    """保存用户订单"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.SaveOrderSerializer

    def get(self, request, order_id):
        try:
            order = OrderInfo.objects.get(user=request.user, order_id=order_id)
        except OrderInfo.DoesNotExist:
            return Response({'message': '查询失败'}, status=status.HTTP_400_BAD_REQUEST)

        if order:
            serializer = serializers.OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        try:
            order = OrderInfo.objects.filter(user=request.user, order_id=order_id, status__in=(1, 4, 5))
        except OrderInfo.DoesNotExist:
            return Response({'message': '查询失败'}, status=status.HTTP_400_BAD_REQUEST)
        if order:
            order.delete()
            return Response({'message': '删除成功!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': '当前订单不允许删除'},status=status.HTTP_400_BAD_REQUEST)


class ListOrderView(ListAPIView):
    """查询全部订单"""
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.query_params.get('status')

        if status == '0':
            return OrderInfo.objects.filter(user_id=self.request.user.id).order_by('-create_time')
        else:
            return OrderInfo.objects.filter(user_id=self.request.user.id, status=int(status)).order_by('-create_time')


class OrderGoodsCommentsView(ListAPIView):
    """当前商品的全部评论信息"""
    serializer_class = serializers.OrderGoodsCommentSerializer

    def get_queryset(self):
        sku_id = self.kwargs['sku_id']
        return OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')


class ConfirmReceiptView(APIView):
    """确认收货"""
    permission_classes = [IsAuthenticated]

    def put(self, request, order_id):
        order = None
        try:
            order = OrderInfo.objects.filter(order_id=order_id, user=request.user, status__in=(2, 3)).update(status=4)
        except Exception as e:
            logger.warning(e)
        if order:
            return Response({'message': '收货成功'})
        else:
            return Response({'message': '收货失败'})


class CommentView(GenericAPIView):
    """修改商品"""

    def put(self, request):
        serializer = serializers.CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        goods_id = data['id']
        sku_id = data['sku_id']
        order_id = data['order_id']
        score = data['score']
        is_anonymous = data.get('is_anonymous'),
        if is_anonymous == (True,):
            is_anonymous = True
        else:
            is_anonymous = False
        comment = data['comment']

        goods = OrderGoods.objects.get(id=goods_id, sku_id=sku_id,order_id=order_id)
        if goods.is_commented == 1:
            return Response({'message': '商品已评价'}, status=status.HTTP_400_BAD_REQUEST)
        goods.score = score
        goods.is_anonymous = is_anonymous
        goods.comment = comment
        goods.is_commented = 1
        goods.order.status = OrderInfo.ORDER_STATUS_ENUM['FINISHED']
        goods.order.save()
        goods.save()
        if not goods:
            return Response({'message': '评论失败'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': '评论成功'})




