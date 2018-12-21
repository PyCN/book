from django.conf.urls import url
from . import views

urlpatterns = [
    url('^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
    url('^payment/status/$', views.PaymentStatusView.as_view()),
]