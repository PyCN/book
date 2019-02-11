import xadmin
from xadmin import views
from . import models


class BaseSetting(object):
    """xadmin的基本配置"""
    enable_themes = True  # 开启主题切换功能
    use_bootswatch = True


class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "美多商城运营管理系统"  # 设置站点标题
    site_footer = "美多商城集团有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠


class SKUAdmin(object):
    # model_icon = 'fa fa-gift'
    list_display = ['id', 'name', 'price', 'stock', 'sales', 'comments']
    search_fields = ['id', 'name']
    list_filter = ['category']
    list_editable = ['price', 'stock']
    show_detail_fields = ['name']
    readonly_fields = ['sales', 'comments']

    def save_models(self):
        # 保存数据对象
        obj = self.new_obj
        obj.save()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUImageAdmin(object):
    def save_models(self):
        obj = self.new_obj
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)
        sku = obj.sku
        # 设置默认图片
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url

    def delete_model(self):
        obj = self.obj
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class GoodsCategoryAdmin(object):
    list_display = ['id', 'name', 'parent']
    list_filter = ['parent']
    search_fields = ['name']


class GoodsChannelAdmin(object):
    list_display = ['id', 'group_id', 'category', 'url', 'sequence']


class AdvertiseCategoryAdmin(object):
    list_display = ['id', 'name']


class AdvertiseAdmin(object):
    list_display = ['id', 'category', 'sku']


class KeyWordAdmin(object):
    list_display = ['id', 'name']


# 全局注册
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)

# 商品注册
xadmin.site.register(models.Category, GoodsCategoryAdmin)
xadmin.site.register(models.Channel, GoodsChannelAdmin)
xadmin.site.register(models.SKU, SKUAdmin)
xadmin.site.register(models.SKUImage, SKUImageAdmin)
xadmin.site.register(models.AdvertiseCategory, AdvertiseCategoryAdmin)
xadmin.site.register(models.Advertise, AdvertiseAdmin)
xadmin.site.register(models.KeyWord, KeyWordAdmin)
