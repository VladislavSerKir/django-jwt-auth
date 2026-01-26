from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(
        source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'role',
                  'role_display', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('name', 'email', 'password')

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

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        return user


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'role')
        read_only_fields = ('id', 'email')
