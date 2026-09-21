from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

urlpatterns = [
    # Health check: public GET request
    # Response body: status is "healthy"
    path("api/health/", views.HealthCheckView.as_view(), name="health-check"),

    # GET /api/user-profile/ [JWT] -> {id, contact, email, last_message}
    # POST /api/user-profile/ [public], body: {contact, email, password}
    #   -> 201 {contact, email}; PUT [JWT], body: {contact?, email?, password?}
    #   -> {id, contact, email, last_message}; DELETE [JWT] -> 204
    path("api/user-profile/", views.UserProfileView.as_view(), name="user-profile"),

    # GET /api/sign-in/ [JWT] -> {id, contact, email, last_message}
    # POST /api/sign-in/ [public], body: {email, password}
    #   -> 200 {refresh, access, user: {id, email, contact}}
    path("api/sign-in/", views.SignInView.as_view(), name="sign-in"),

    # POST /api/forgot-password/ [public], body: {email}
    # Response body: message is "Password reset OTP sent."
    path("api/forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),

    # POST /api/reset-password/ [public], body: {email, otp, new_password}
    # Response body: message is "Password reset successful."
    path("api/reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),

    # GET /api/messages/ [JWT], header: receiver=<user id> -> [{id, sender, receiver, content}]
    # POST /api/messages/ [JWT], body: {receiver, content}
    #   -> 201 {id, sender, receiver, content}
    path("api/messages/", views.MessageView.as_view(), name="messages"),

    # GET /api/contacts/ [JWT] -> [{id, contact, email, last_message}]
    path("api/contacts/", views.ContactView.as_view(), name="contacts"),

    # GET /api/all-users/ [JWT] -> [{id, contact, email, last_message}]
    path("api/all-users/", views.AllUsersView.as_view(), name="all-users"),

    # POST /api/sign-up-otp/ [public], body: {email, otp}
    #   -> 200 {refresh, access, user: {id, email, contact}}
    path("api/sign-up-otp/", views.VerifyUserOTPView.as_view(), name="sign-up-otp"),

    # POST /api/token/ [public], body: {email, password} -> {refresh, access}
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),

    # DO NOT USE this endpoint for now use api/sign-in/ instend
    # POST /api/token/refresh/ [public], body: {refresh} -> {access}
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # POST /api/token/verify/ [public], body: {token} -> 200 {}
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # POST /google-login/ [public], body: {code}
    #   -> 200 {message, refresh, access, user: {id, email, contact}}
    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
]
