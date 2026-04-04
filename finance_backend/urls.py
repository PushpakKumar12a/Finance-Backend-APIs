"""
Root URL configuration for the finance_backend project.
All API endpoints are prefixed with /api/.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    "API index — lists all available endpoints."
    return Response({
        'message': 'Finance Data Processing & Access Control API',
        'docs': {
            'swagger': '/api/docs/',
            'redoc': '/api/docs/redoc/',
            'openapi_schema': '/api/docs/schema/',
        },
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'refresh': '/api/auth/refresh/',
                'profile': '/api/auth/me/',
            },
            'users': {
                'list': '/api/users/',
                'detail': '/api/users/{id}/',
            },
            'records': {
                'list_create': '/api/records/',
                'detail': '/api/records/{id}/',
            },
            'dashboard': {
                'summary': '/api/dashboard/summary/',
                'category_breakdown': '/api/dashboard/category-breakdown/',
                'trends': '/api/dashboard/trends/',
                'recent_activity': '/api/dashboard/recent-activity/',
            },
        },
    })


urlpatterns = [
    path('admin/', admin.site.urls),

    # API docs (Swagger & ReDoc)
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('api/', api_root, name='api-root'),
    path('api/', include('accounts.urls')),
    path('api/', include('records.urls')),
    path('api/', include('dashboard.urls')),
]
