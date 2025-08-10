from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls"), name="api-auth"),
    path("", include("zserver.urls")),
    path("health-check/", views.HealthCheckView.as_view(), name="health-check"),
    path("api/", views.api_index_view, name="api-index"),
]
