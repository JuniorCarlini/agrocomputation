from users.views import home
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls import handler404

handler404 = 'users.views.custom_404'

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Home
    path('', home, name='home'),

    # Users
    path("users/", include("users.urls")),

    # Modules
    path("irrigation/", include("irrigation.urls")),
    path("station/", include("station.urls")),
]
