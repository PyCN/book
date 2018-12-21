from django_redis import get_redis_connection
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from goods.models import SKU
from goods.serializers import SKUSerializer
from carts.utils import merge_cart_cookie_to_redis
from .models import User
from .import serializers
from . import constants


class UserAuthorizeView(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):

        # 调用父类的方法，获取drf jwt扩展默认的认证用户处理结果
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)

        # 仿照drf jwt扩展对于用户登录的认证方式，判断用户是否认证登录成功
        # 如果用户登录认证成功，则合并购物车
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, user, response)
        return response


class UsernameCountView(APIView):
    """用户名是否存在：count：1 存在 count：0 不存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class MobileCountView(APIView):
    """手机号是否存在：count：1 存在 count：0 不存在"""
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


# url(r'^users/$', views.UserView.as_view()),
class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    # 视图使用的序列化器
    serializer_class = serializers.CreateUserSerializer


class UserPasswordView(UpdateAPIView):
    """用户密码修改"""
    serializer_class = serializers.UserPasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserDetailView(RetrieveAPIView):
    """用户详情信息查询"""
    serializer_class = serializers.UserDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """用户邮箱修改"""
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    """用户邮箱验证"""

    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        # 验证token
        user = User.check_email_url(token)
        # 判断用户是否存在
        if not user:
            return Response({'message': '链接无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 保存邮箱激活状态
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == 'title':
            return serializers.AddressTitleSerializer
        else:
            return serializers.UserAddressSerializer

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        query_set = self.get_queryset()
        serializer = self.get_serializer(query_set, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data
        })

    # delete /addresses/<pk>/
    def destroy(self, request, pk=None):
        """
        处理删除
        """
        address = self.get_object()
        # 进行逻辑删除
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        return self.update(request)


class UserBrowsingHistoryView(CreateAPIView):
    """
    用户浏览历史
    """
    serializer_class = serializers.AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取用户浏览历史商品
        :param request:
        :return:
        """
        # 获取用户id
        user_id = self.request.user.id

        # 获取连接
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)
        skus = []
        # 与用户浏览记录保持一致,需要遍历sku_ids
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        serializer = SKUSerializer(skus, many=True)
        return Response(serializer.data)

