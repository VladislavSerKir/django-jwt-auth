from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from .enums import Role

from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer,
    LoginSerializer, UserRoleUpdateSerializer
)
from .middleware import method_roles


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        data = serializer.validated_data.copy()
        data.pop('role', None)
        serializer.save(**data)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()

        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            print(f"DeleteAccountView: {e}")
            pass

        return Response(
            {'message': 'Account deactivated successfully'},
            status=status.HTTP_200_OK
        )


@method_roles(Role.ADMIN)
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@method_roles(Role.ADMIN)
class AdminUpdateUserRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserRoleUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
