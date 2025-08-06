from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegisterationSerializer(serializers.ModelSerializer ):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        """Create a new user with hashed password."""
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for User detail view."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']