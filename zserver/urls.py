from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

urlpatterns = [
    # Health check endpoint for deployment monitoring
    path("api/health/", views.HealthCheckView.as_view(), name="health-check"),

    # API endpoints for React frontend
    path("api/user-profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("api/sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("api/forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("api/messages/", views.MessageView.as_view(), name="messages"),
    path("api/contacts/", views.ContactView.as_view(), name="contacts"),
    path("api/all-users/", views.AllUsersView.as_view(), name="all-users"),
    path("api/sign-up-otp/", views.VerifyUserOTPView.as_view(), name="sign-up-otp"),

    # JWT Token endpoints (using built-in simplejwt views)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
]
