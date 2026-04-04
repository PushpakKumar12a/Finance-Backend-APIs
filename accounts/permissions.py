"""
Role-based permission classes for DRF views.

Hierarchy: Admin > Analyst > Viewer
- IsAdmin:           only admin
- IsAnalystOrAbove:  analyst or admin
- IsViewerOrAbove:   any authenticated user (viewer, analyst, admin)

These are composed in views via `permission_classes` to enforce RBAC.
"""

from rest_framework.permissions import BasePermission

from accounts.models import User

class IsAdmin(BasePermission):
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsAnalystOrAbove(BasePermission):
    message = 'Analyst or Admin access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.Role.ANALYST, User.Role.ADMIN)
        )


class IsViewerOrAbove(BasePermission):
    message = 'Authentication required.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
