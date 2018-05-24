from django.conf.urls import url
from scientist import views

urlpatterns = [
                       url(r'^$', views.scientist_list, name='scientist_list'),
                       url(r'^(?P<scientist_name>[\w.%+-@]+)/$', views.scientist_detail, name='scientist_detail'),
                       url(r'^api/contact$', views.api_contact, name='api_contact'),
]
