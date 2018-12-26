import xadmin
from . import models
# Register your models here.


class OAuthQQUserAdmin(object):
    """广告内容类别站点显示"""
    list_display = ['id', 'user', 'openid']
    search_fields = ['id', 'user']


xadmin.site.register(models.OAuthQQUser, OAuthQQUserAdmin)
