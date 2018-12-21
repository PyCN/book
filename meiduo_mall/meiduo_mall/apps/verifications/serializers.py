from django_redis import get_redis_connection
from rest_framework import serializers


class ImageCodeCheckSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()  # 验证UUID
    text = serializers.CharField(max_length=4, min_length=4)  # 验证图片验证码

    def validate(self, attrs):
        # 校验图片验证码
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        redis_conn = get_redis_connection('verify_codes')
        real_image_code = redis_conn.get("img_%s" % image_code_id)
        if not real_image_code:
            raise serializers.ValidationError('图片验证码已过期')
        else:
            redis_conn.delete('img_%s' % image_code_id)

        real_image_code = real_image_code.decode()
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError('图片验证码有误')

        # 判断是否在60内
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('请求的次数过于频繁')
        return attrs
