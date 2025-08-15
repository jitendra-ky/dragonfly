from django.urls import path, include

urlpatterns = [
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # endpoints that it provide are
    # dj-rest-auth/ login/?$ [name='rest_login']
    # dj-rest-auth/ logout/?$ [name='rest_logout']
    # dj-rest-auth/ user/?$ [name='rest_user_details']
    # although password reset endpoints added but they need some debugging.
    # dj-rest-auth/ password/reset/?$ [name='rest_password_reset']
    # dj-rest-auth/ password/reset/confirm/?$ [name='rest_password_reset_confirm']
    # dj-rest-auth/ password/change/?$ [name='rest_password_change']
]