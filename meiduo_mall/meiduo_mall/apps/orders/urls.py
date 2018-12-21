from django.conf.urls import url
from . import views

urlpatterns = [
    url('^orders/settlement/$', views.OrderSettlementView.as_view()),
    url('^orders/$', views.OrderView.as_view()),
    url('^orders/(?P<order_id>\d+)/$', views.OrderView.as_view()),
    url('^orders/list/$', views.ListOrderView.as_view()),
    url('^comments/(?P<sku_id>\d+)/$', views.OrderGoodsCommentsView.as_view()),
    url('^confirm/(?P<order_id>\d+)/$', views.ConfirmReceiptView.as_view()),
    url('^comment/$', views.CommentView.as_view()),

]