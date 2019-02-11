import xadmin
from . import models
# Register your models here.


class ContentCategoryAdmin(object):
    """广告内容类别站点显示"""
    list_display = ['id', 'name', 'key']
    search_fields = ['id', 'name']


class ContentAdmin(object):
    """广告内容站点显示"""
    list_display = ['id', 'category', 'title', 'url', 'image', 'text', 'sequence', 'status']
    search_fields = ['id', 'title']
    list_filter = ['category']


xadmin.site.register(models.ContentCategory, ContentCategoryAdmin)
xadmin.site.register(models.Content, ContentAdmin)
