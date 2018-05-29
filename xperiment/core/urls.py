from django.conf.urls import url
from core import views

urlpatterns = [

                       url(r'^avatar/upload/$', views.upload_avatar, name='upload_avatar'),
                       url(r'^$', views.home, name='home'),
]
