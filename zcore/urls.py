from django.urls import path

from .views import HealthCheckView

urlpatterns = [
    # Health check: public GET request body status "healthy"
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
]
