from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),

    path("signin/", views.SignInTemplateView.as_view(), name="sign-in-page"),
    path("signup/", views.SignUpTemplateView.as_view(), name="sign-up-page"),
    path("forgot-password/",
         views.ForgotPasswordTemplateView.as_view(),
         name="forgot-password-page"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/user-profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("api/sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("api/forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("api/reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("api/messages/", views.MessageView.as_view(), name="messages"),
    path("api/contacts/", views.ContactView.as_view(), name="contacts"),
    path("api/all-users/", views.AllUsersView.as_view(), name="all-users"),
    path("api/sign-up-otp/", views.VerifyUserOTPView.as_view(), name="sign-up-otp"),

    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
]
