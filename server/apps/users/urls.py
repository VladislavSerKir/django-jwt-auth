from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView,
    UserProfileView, DeleteAccountView,
    AdminUserListView, AdminUpdateUserRoleView
)

urlpatterns = [
    # Public
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Admin endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>/role/',
         AdminUpdateUserRoleView.as_view(), name='admin-update-role'),
]
