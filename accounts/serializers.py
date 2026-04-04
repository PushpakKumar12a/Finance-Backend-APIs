from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import User

class UserRegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        # New registrations always get the Viewer role
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=User.Role.VIEWER,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'role',
            'is_active', 'date_joined', 'last_login',
        ]
        read_only_fields = fields


class UserMgmtSerializer(serializers.ModelSerializer):
    """
    Admin-only serializer for updating user role and status.
    Only exposes the fields an admin should be able to change.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'email', 'username', 'date_joined']

    def validate_role(self, value):
        if value not in dict(User.Role.choices):
            raise serializers.ValidationError(
                f'Invalid role. Choose from: {", ".join(dict(User.Role.choices).keys())}'
            )
        return value
