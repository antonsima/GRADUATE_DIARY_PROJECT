from django.urls import path
from django.views.generic import TemplateView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserProfileView, logout_view

app_name = UsersConfig.name

urlpatterns = [
    # API endpoints
    path("api/login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("api/register/", UserCreateAPIView.as_view(), name="register"),
    path("api/token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("api/profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/logout/", logout_view, name="logout"),

    # HTML pages
    path("", TemplateView.as_view(template_name="users/index.html"), name="index"),
    path("register/", TemplateView.as_view(template_name="users/register.html"), name="register_page"),
    path("login/", TemplateView.as_view(template_name="users/login.html"), name="login_page"),
    path("profile/", TemplateView.as_view(template_name="users/profile.html"), name="profile_page"),
    path("logout/", TemplateView.as_view(template_name="users/logout.html"), name="logout_page"),
]
