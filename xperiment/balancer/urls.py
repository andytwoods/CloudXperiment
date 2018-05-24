from django.conf.urls import url
from balancer import views


urlpatterns = [
    url(r'^balancer/(?P<group_id>\w+)/$', views.change_orderings, name='balancer'),
    url(r'^balancer/(?P<group_id>\w+)/delete/$', views.delete_order, name='delete_order'),
    url(r'^balancer/(?P<group_id>\w+)/modify/$', views.order_batch_modify_order, name='order_batch_modify_order'),
    url(r'^balancer/(?P<group_id>\w+)/add/$', views.order_batch_add, name='order_batch_add'),
]
