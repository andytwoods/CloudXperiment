from django.conf.urls import url
from lab import views
from django.conf import settings
from django.conf.urls import include, url

urlpatterns = [
       #url(r'^$', views.lab_list, name='lab_list'),
       url(r'^lab/(?P<lab_id>\d+)/(?P<slug>[\w-]+)/detail/$', views.lab_detail, name='lab_detail'),
       url(r'^lab/manage/add/$', views.add_edit_lab, name='add_lab'),
       url(r'^lab/manage/(?P<lab_id>\d+)/edit/$', views.add_edit_lab, name='edit_lab'),
       url(r'^lab/member/add/$', views.add_member, name='add_member'),
       url(r'^lab/member/delete/$', views.delete_member, name='delete_member'),
       url(r'^lab/logo/upload/$', views.upload_logo, name='upload_logo'),
       url(r'^lab/(?P<lab_id>\d+)/payment/$', views.payment, name='payment'),
       url(r'^lab/(?P<lab_id>\d+)/payment/complete/$', views.payment_complete, name='payment_complete'),
       url(r'^lab/(?P<lab_id>\d+)/balancer/$', views.manage_orderings, name='lab_balancer'),
       url(r'^lab/(?P<lab_id>\d+)/balancer/delete/$', views.delete_order, name='lab_balancer_delete_order'),
       url(r'^lab/(?P<lab_id>\d+)/balancer/add/$', views.balancer_add, name='lab_balancer_order_add'),
       url(r'^lab/(?P<lab_id>\d+)/balancer/update/$', views.balancer_update, name='lab_balancer_order_update'),
       url(r'^lab/(?P<lab_id>\d+)/balancer/edit/(?P<balance_id>\d+)/$', views.balancer_edit,
           name='lab_balancer_order_edit'),
       url(r'^balance/(?P<slug>\w+)/$', views.balancer_url, name='lab_balancer_url'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
