from allauth.account.views import LoginView
from django.conf import settings
from django.conf.urls import include, url

from django.contrib import admin
from django.views.static import serve

from scientist.views import update_profile

admin.autodiscover()

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('core.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^profile/$', update_profile, name='update_profile'),
    url(r'^scientist/', include('scientist.urls')),
    url(r'', include('lab.urls')),
    url(r'', include('experiment.urls')),
    url(r'', include('balancer.urls')),

]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
