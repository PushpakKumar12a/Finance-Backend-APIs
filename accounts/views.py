"""
Views for authentication and user management.

Public endpoints: register, login (token), refresh
Authenticated endpoints: /me (profile)
Admin endpoints: user list, user detail/update/delete
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdmin
from accounts.serializers import (
    UserMgmtSerializer,
    UserRegSerializer,
    UserSerializer,
)

# Public: Registration

@extend_schema(tags=['Auth'])
class RegAPI(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Create a new user account. New users are assigned the Viewer role by default.
    """
    serializer_class = UserRegSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'User registered successfully.',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

# Authenticated: Profile

@extend_schema(tags=['Auth'])
class ProfileAPI(APIView):
    """
    GET /api/auth/me/
    Returns the profile of the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

# Admin: User management

@extend_schema(tags=['Users'])
class UserListAPI(generics.ListAPIView):
    """
    GET /api/users/
    Admin-only: List all users with optional search by email/username.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    search_fields = ['email', 'username']


@extend_schema(tags=['Users'])
class UserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/users/<id>/
    Admin-only: View, update role/status, or delete a user.
    """
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UserMgmtSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'error': True, 'message': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False  # Soft deactivation instead of hard delete
        user.save(update_fields=['is_active'])
        return Response(
            {'message': 'User has been deactivated.'},
            status=status.HTTP_200_OK,
        )