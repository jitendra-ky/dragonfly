from django.urls import path

from . import views

urlpatterns = [
    path("user-profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("sign-up-otp/", views.SignUpOTPView.as_view(), name="sign-up-otp"),
]
