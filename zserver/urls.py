from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),

    path("signin/", views.SignInTemplateView.as_view(), name="sign-in-page"),
    path("signup/", views.SignUpTemplateView.as_view(), name="sign-up-page"),

    path("api/user-profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("api/sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("api/sign-up-otp/", views.SignUpOTPView.as_view(), name="sign-up-otp"),
    path("api/forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),

    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
]
