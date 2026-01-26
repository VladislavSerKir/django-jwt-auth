from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        "User account is disabled.")
                data['user'] = user
                return data
            raise serializers.ValidationError(
                "Unable to log in with provided credentials.")
        raise serializers.ValidationError(
            "Must include 'email' and 'password'.")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'role', 'is_active', 'created_at')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'role',
                  'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'name', 'role')
        extra_kwargs = {
            'email': {'required': False},
            'name': {'required': False},
        }

    def validate_role(self, value):
        request = self.context.get('request')
        if request and request.user.role != Role.ADMIN.value:
            raise serializers.ValidationError("Only admin can change role.")
        return value
