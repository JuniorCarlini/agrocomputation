from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from django.conf.urls.static import static

handler404 = 'users.views.custom_404'

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Home
    path('', include("comum.urls")),

    # Users
    path("users/", include("users.urls")),

    # Modules
    path("irrigation/", include("irrigation.urls")),
    path("station/", include("station.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
