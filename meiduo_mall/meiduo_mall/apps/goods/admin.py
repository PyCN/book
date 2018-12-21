from django.contrib import admin
from . import models


admin.site.site_header = '潇潇商城'
admin.site.site_title = '潇潇商城'
admin.site.index_title = '欢迎使用潇潇商城'


class GoodsChannelAdmin(admin.ModelAdmin):
    list_filter = ['group_id']


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUSpecificationAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)

    def delete_model(self, request, obj):
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUImageAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)
        sku = obj.sku
        # 设置默认图片
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url

    def delete_model(self, request, obj):
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel, GoodsChannelAdmin)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)