import xadmin
from . import models


class OrderAdmin(object):
    list_display = ['order_id', 'create_time', 'total_amount', 'pay_method', 'status']
    refresh_times = [3, 5]  # 可选以支持按多长时间(秒)刷新页面
    data_charts = {
        "order_amount": {'title': '订单金额', "x-field": "create_time", "y-field": ('total_amount',),
                         "order": ('create_time',)},
        "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
                        "order": ('create_time',)},
    }


class OrderGoodsAdmin(object):
    list_display = ['id', 'order', 'sku', 'count', 'price', 'comment', 'score', 'is_anonymous', 'is_commented']
    search_fields = ['id', 'order']


xadmin.site.register(models.OrderGoods, OrderGoodsAdmin)
xadmin.site.register(models.OrderInfo, OrderAdmin)