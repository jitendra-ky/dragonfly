from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    
    path("api/user-profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("api/sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("api/sign-up-otp/", views.SignUpOTPView.as_view(), name="sign-up-otp"),
]
