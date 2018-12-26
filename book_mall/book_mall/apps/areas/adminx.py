import xadmin
from . import models
# Register your models here.


class AreaAdmin(object):
    """商品分类站点显示"""
    list_display = ['id', 'name', 'parent']
    search_fields = ['id', 'name']


xadmin.site.register(models.Area, AreaAdmin)
