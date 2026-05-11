"""URL configuration for fondosong project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("organizaciones.urls")),
    path("admin/", admin.site.urls),
]
