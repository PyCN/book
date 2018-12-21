from django.conf import settings
import urllib.parse
from urllib.request import urlopen
import logging
import json
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from . import constants
from .exceptions import OAuthQQAPIError

logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    QQ认证辅助工具类
    """
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id if client_id else settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri if redirect_uri else settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE
        self.client_secret = client_secret if client_secret else settings.QQ_CLIENT_SECRET

    def get_login_url(self):
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        url += urllib.parse.urlencode(params)
        return url

    def get_access_token(self, code):

        url = 'https://graph.qq.com/oauth2.0/token?'

        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }

        url += urllib.parse.urlencode(params)

        try:
            # 发送请求
            resp = urlopen(url)

            # 读取响应体数据
            resp_data = resp.read()  # bytes
            resp_data = resp_data.decode()  # str
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14

            # 解析 access_token
            resp_dict = urllib.parse.parse_qs(resp_data)
            access_token = resp_dict.get('access_token')
        except Exception as e:
            logger.error('获取access_token异常：%s' % e)
            raise OAuthQQAPIError
        else:
            return access_token[0]

    def get_openid(self, access_token):
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:
            # 发送请求
            resp = urlopen(url)

            # 读取响应体数据
            resp_data = resp.read()  # bytes
            resp_data = resp_data.decode()  # str

            # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;

            # 解析
            resp_data = resp_data[10:-4]
            resp_dict = json.loads(resp_data)
        except Exception as e:
            logger.error('获取openid异常：%s' % e)
            raise OAuthQQAPIError
        else:
            openid = resp_dict.get('openid')

            return openid

    def generate_bind_user_access_token(self, openid):
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({'openid': openid})
        return token.decode()

    @staticmethod
    def check_bind_user_access_token(access_token):
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data['openid']



































