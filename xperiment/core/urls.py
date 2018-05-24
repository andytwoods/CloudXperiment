from django.conf.urls import url
from core import views

urlpatterns = [
                       url(r'^signup/ajax/$', views.ajax_signup, name='ajax_signup'),
                       url(r'^avatar/upload/$', views.upload_avatar, name='upload_avatar'),
                       url(r'^$', views.home, name='home'),
]
