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
    search_fields = ['id','name']
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


class SKUSpecificationAdmin(object):
    def save_models(self):
        # 保存数据对象
        obj = self.new_obj
        obj.save()

        # 补充自定义行为
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self):
        # 删除数据对象
        obj = self.obj
        sku_id = obj.sku.id
        obj.delete()

        # 补充自定义行为
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


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


class GoodsAdmin(object):
    list_display = ['id', 'name', 'brand', 'category1', 'category2', 'category3']
    list_filter = ['brand', 'category1', 'category2', 'category3']


class GoodsSpecificationAdmin(object):
    list_display = ['id', 'goods', 'name']
    list_filter = ['goods']


class SpecificationOptionAdmin(object):
    list_display = ['id', 'spec', 'value']
    list_filter = ['spec']


class BrandAdmin(object):
    list_display = ['id', 'name', 'logo', 'first_letter']


class GoodsChannelAdmin(object):
    list_display = ['id', 'group_id', 'category', 'url', 'sequence']


# 全局注册
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)


# 商品注册
xadmin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
xadmin.site.register(models.GoodsChannel, GoodsChannelAdmin)
xadmin.site.register(models.Goods, GoodsAdmin)
xadmin.site.register(models.Brand, BrandAdmin)
xadmin.site.register(models.GoodsSpecification, GoodsSpecificationAdmin)
xadmin.site.register(models.SpecificationOption, SpecificationOptionAdmin)
xadmin.site.register(models.SKU, SKUAdmin)
xadmin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
xadmin.site.register(models.SKUImage, SKUImageAdmin)