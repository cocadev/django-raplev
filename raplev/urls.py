from django.urls import path, include
from django.contrib import admin
from cadmin import views as cadmin_views
from django.views.generic import RedirectView

urlpatterns = [
    path('cadmin/', include('cadmin.urls')),
    path('super-admin/', cadmin_views.super_admin_view),
    path('super-admin/', admin.site.urls),
    path('', include('theme.urls')),
    path('api/', include('apis.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('<slug:link>/', cadmin_views.go_page),
]

from django.conf import settings
# if settings.DEBUG:
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)