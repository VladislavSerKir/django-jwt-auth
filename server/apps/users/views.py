from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from apps.users.middleware import require_roles


from .enums import Role
from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer,
    UserListSerializer, UserDetailSerializer,
    UserUpdateSerializer
)


class RegisterView(APIView):
    """User registration"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User authentication"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    """Refresh access token"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)

            user_id = refresh.payload.get('user_id')
            user = get_object_or_404(User, id=user_id)

            if not user.is_active:
                return Response(
                    {'error': 'Account is deactivated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            new_refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(new_refresh),
                'access': str(new_refresh.access_token),
            })

        except Exception:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """Logout with blacklisting both tokens"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                access_token_str = auth_header.split(' ')[1]

                try:
                    access_token = AccessToken(access_token_str)

                    jti = access_token['jti']

                    outstanding_token, created = OutstandingToken.objects.get_or_create(
                        jti=jti,
                        defaults={
                            'token': str(access_token),
                            'created_at': timezone.now(),
                            'expires_at': timezone.datetime.fromtimestamp(access_token['exp'], tz=timezone.utc),
                            'user': request.user,
                        }
                    )

                    BlacklistedToken.objects.get_or_create(
                        token=outstanding_token)

                except TokenError as e:
                    print(f"Access token error: {e}")

            return Response(
                {'message': 'Successfully logged out. Tokens invalidated.'},
                status=status.HTTP_200_OK
            )

        except TokenError as e:
            return Response(
                {'error': f'Invalid token: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserListView(APIView):
    """Get user list"""
    permission_classes = [permissions.IsAuthenticated]

    @require_roles(Role.ADMIN)
    def get(self, request):
        users = User.objects.filter()
        serializer = UserListSerializer(users, many=True)
        return Response({'users': serializer.data})


class UserDetailView(APIView):
    """Get/update/delete user"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.role != Role.ADMIN.value and request.user.id != user.id:
            return Response(
                {'error': 'You do not have permission to access this user'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.role != Role.ADMIN.value and request.user.id != user.id:
            return Response(
                {'error': 'You do not have permission to update this user'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserUpdateSerializer(
            user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.role != Role.ADMIN.value and request.user.id != user.id:
            return Response(
                {'error': 'You do not have permission to delete this user'},
                status=status.HTTP_403_FORBIDDEN
            )

        user.is_active = False
        user.save()

        return Response({'id': user_id}, status=status.HTTP_200_OK)
