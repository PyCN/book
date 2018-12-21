from drf_haystack.viewsets import HaystackViewSet
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import SKU, GoodsCategory, GoodsChannel
from . import serializers
from .utils import get_categories
from . import constants


class SKUListView(ListAPIView):
    """
    查询三级分类下的所有商品
    """
    serializer_class = serializers.SKUSerializer

    # 过滤
    filter_backends = (OrderingFilter,)
    ordering_fields = ('create_time', 'price', 'sales')

    # 分页统一设置

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class GoodsCategoryListView(CacheResponseMixin, GenericAPIView):

    def get(self, request):
        return Response(get_categories())


class HotSKUListView(ListAPIView):
    serializer_class = serializers.SKUSerializer
    pagination_class = None
    # 分页统一设置

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[0: constants.HOT_GOODS_MAX_LIMIT]


class BreadcrumbView(APIView):
    """面包屑导航栏"""
    def get(self, request, category_id):

        context = {}
        try:
            cat3 = GoodsCategory.objects.get(id=category_id)

            context['cat3'] = {'name': cat3.name}
            cat2 = GoodsCategory.objects.get(id=cat3.parent_id)
            context['cat2'] = {'name': cat2.name}
            cat1 = GoodsCategory.objects.get(id=cat2.parent_id)
            gc = GoodsChannel.objects.get(category_id=cat1.id)
        except Exception as e:
            return Response('分类不存在', status=status.HTTP_400_BAD_REQUEST)
        else:
            context['cat1'] = {
                'url': gc.url,
                'category': {'name': cat1.name }
            }
            return Response(context)


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]
    serializer_class = serializers.SKUIndexSerializer
