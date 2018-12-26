from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    url('^categories/$', views.GoodsCategoryListView.as_view()),
    url('^categories/(?P<category_id>\d+)/$', views.BreadcrumbView.as_view()),
    url('^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
    url('^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    url('^add_data/$', views.AddDataView.as_view()),
]

router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')
urlpatterns += router.urls

