from django.conf.urls import url
from . import views

urlpatterns = [
    url('^qq/authorization/$', views.QQAuthURLView.as_view()),
    url('^qq/user/$', views.QQAuthUserView.as_view()),
]
