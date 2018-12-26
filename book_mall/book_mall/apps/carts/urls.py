from django.conf.urls import url
from . import views

urlpatterns = [
    url('^cart/$', views.CartView.as_view()),
    url('^cart/selection/$', views.CartSelectionView.as_view())
]