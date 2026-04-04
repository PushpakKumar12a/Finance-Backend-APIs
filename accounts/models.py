"""
User model with role-based access.

Design decisions:
- Extends AbstractUser to leverage Django's built-in auth (password hashing, etc.)
- Uses email as the login identifier instead of username
- Role is a simple CharField with three choices — sufficient for three fixed roles
  and avoids the complexity of a separate Role/Permission table
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        VIEWER = 'viewer', 'Viewer'
        ANALYST = 'analyst', 'Analyst'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text='Determines the user\'s access level in the system.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def is_viewer(self):
        return self.role == self.Role.VIEWER

    @property
    def is_analyst(self):
        return self.role == self.Role.ANALYST

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN
