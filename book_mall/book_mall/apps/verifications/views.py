import random

from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

import logging
from book_mall.utils.captcha.captcha import captcha
from rest_framework.views import APIView

from . import constants
from .serializers import ImageCodeCheckSerializer

# 获取日志
logger = logging.getLogger('django')


class ImageCodeView(APIView):
    """生成图片验证码视图"""

    def get(self, request, image_code_id):
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        # 将内容保存到redis
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        logger.info('图片验证码：%s' % text)
        # 返回数据
        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    """短信验证码视图"""
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 校验参数
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        logger.info("短信验证码：%s" % sms_code)
        # 保存到redis
        redis_conn = get_redis_connection('verify_codes')
        # redis管道
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 让管道通知redis执行命令
        pl.execute()

        # 发送短信
        # expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        # sms_tasks.send_sms_code.delay(mobile, sms_code, expires, constants.SMS_CODE_TEMP_ID)
        return Response({'message': 'OK'})



