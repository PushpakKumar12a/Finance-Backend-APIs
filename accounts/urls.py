"URL configuration for the accounts app."

from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts import views


# Tag the third-party JWT views so they appear under "Auth" in Swagger
LoginView = extend_schema(tags=['Auth'])(TokenObtainPairView)
RefreshView = extend_schema(tags=['Auth'])(TokenRefreshView)

urlpatterns = [
    # ---- Auth ----
    path('auth/register/', views.RegAPI.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/refresh/', RefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', views.ProfileAPI.as_view(), name='auth-profile'),

    # ---- Admin: User management ----
    path('users/', views.UserListAPI.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailAPI.as_view(), name='user-detail'),
]
