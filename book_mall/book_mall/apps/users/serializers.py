import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_active_email
from goods.models import SKU
from users import constants

from .models import User, Address


class CreateUserSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password2 = serializers.CharField(label='确认密码', write_only=True, min_length=8, max_length=20)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码'
                }
            }
        }

    def validate(self, attrs):
        """用户字段验证"""
        # 用户名校验
        username = attrs['username']
        if re.match(r'^1[3-9]\d{9}$', username):
            raise serializers.ValidationError('用户名不能为手机号')

        # 手机号验证
        mobile = attrs['mobile']
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise serializers.ValidationError('手机号格式错误')

        # 协议验证
        allow = attrs['allow']
        if allow != "true":
            raise serializers.ValidationError('请同意协议')

        # 两次密码校验
        password = attrs['password']
        password2 = attrs['password']
        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 短信验证码校验
        sms_code = attrs['sms_code']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if not real_sms_code:
            raise serializers.ValidationError('短信验证码失效')

        if sms_code != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        # 返回序校验数据
        return attrs

    def create(self, validated_data):
        # 移除数据库模型中不存在的字段
        validated_data.pop('password2', None)
        validated_data.pop('sms_code', None)
        validated_data.pop('allow', None)

        # 保存数据库
        # user = User.objects.create(**validated_data)
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        # 返回数据
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """用户邮箱修改序列化器"""
    class Meta:
        model = User
        fields = ('id', 'email')

    def update(self, instance, validated_data):
        # 更新邮箱信息
        email = validated_data['email']
        instance.email = email
        instance.save()

        # 生成激活url
        email_active_url = instance.general_email_verify_url()

        # 发送邮件
        send_active_email.delay(email, email_active_url)

        # 返回数据
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate(self, attrs):
        count = self.context['request'].user.addresses.count()
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            raise serializers.ValidationError("保存地址数据已达到上限")
        return attrs

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)

    def update(self, instance, validated_data):
        instance.title = validated_data['title']
        instance.save()
        return instance


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label='SKU编号', min_value=1)

    def validate_stu_id(self, value):
        try:
            SKU.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError('商品不存在')
        return value

    def create(self, validated_data):
        """
        用户浏览商品详情时,进行添加
        :param validated_data:
        :return:
        """
        # 获取当前用户的id
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']
        # 使用redis列表保存当前用户浏览商品的sku_id
        redis_conn = get_redis_connection('history')

        # 建立redis管道
        pl = redis_conn.pipeline()

        # 去除用户重复浏览的商品
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 添加用户浏览数据
        pl.lpush('history_%s' % user_id, sku_id)
        # 删除多余的数据,即保留用户最大的浏览记录数
        pl.ltrim('history_%s' % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)

        # 执行管道
        pl.execute()

        # 返回数据
        return validated_data


class UserPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(label='新密码', write_only=True, min_length=8, max_length=20)
    new_password2 = serializers.CharField(label='确认新密码', write_only=True, min_length=8, max_length=20)

    class Meta:
        model = User
        fields = ('id', 'password', 'new_password', 'new_password2')

    extra_kwargs = {
        'password': {
            'write_only': True,
            'min_length': 8,
            'max_length': 20,
            'error_messages': {
                'min_length': '仅允许8-20个字符的密码',
                'max_length': '仅允许8-20个字符的密码'
            }
        }
    }

    def validate(self, attrs):
        password = attrs['password']
        user = self.context['request'].user
        if not user.check_password(password):
            raise serializers.ValidationError('当前密码输入错误')
        # 两次密码校验
        new_password = attrs['new_password']
        new_password2 = attrs['new_password2']
        if new_password != new_password2:
            raise serializers.ValidationError('两次密码不一致')

        if new_password == password:
            raise serializers.ValidationError('修改密码与原密码一致,无须修改')

        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data['new_password']
        instance.set_password(new_password)
        instance.save()
        return instance