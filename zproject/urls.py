from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("zcore.urls")),
    path("", include("zauth.urls")),
    path("", include("zchat.urls")),
]

