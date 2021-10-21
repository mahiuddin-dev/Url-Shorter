from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve as mediaserve
from django.conf.urls.static import static

from url.views import UpdateLink

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls', namespace='Home')),
    path('Account/', include('Account.urls', namespace='Account')),
    path('url/', include('url.urls', namespace='url')),
    path('update_link/', UpdateLink, name='update_link'),
]

urlpatterns.append(url(f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$',
                       mediaserve, {'document_root': settings.MEDIA_ROOT}))

urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)