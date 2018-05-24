from django.conf.urls import patterns, url


urlpatterns = [
                       url(r'^upload/$', 'attachment_upload', name='attachment_upload'),

]