from allauth.account.views import LoginView
from django.conf import settings
from django.conf.urls import include, url

from django.contrib import admin
from django.urls import path
from django.views.static import serve

from scientist.views import update_profile

admin.autodiscover()

urlpatterns = [

    path('banana/', admin.site.urls),
    url('', include('core.urls')),
    url('accounts/', include('allauth.urls')),
    url('profile/', update_profile, name='update_profile'),
    url('scientist/', include('scientist.urls')),
    url('', include('lab.urls')),
    url('', include('experiment.urls')),
    url('', include('balancer.urls')),

]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
