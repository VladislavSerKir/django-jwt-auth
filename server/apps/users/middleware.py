from .enums import Role
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import AnonymousUser
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RBACMiddleware:
    """Role base access middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.user_role = self._get_user_role(request)
        return self.get_response(request)

    def _get_user_role(self, request: HttpRequest) -> Optional[Role]:
        if not hasattr(request, 'user') or not request.user:
            return None

        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            return None

        try:
            return request.user.get_role()
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return None


def method_roles(*roles: Role):
    """
    Декоратор для проверки ролей в class-based views
    Теперь работает правильно с классами
    """
    def decorator(cls):
        original_dispatch = cls.dispatch

        def new_dispatch(self, request, *args, **kwargs):
            user_role = getattr(request, 'user_role', None)

            if user_role is None:
                if hasattr(request.user, 'get_role'):
                    user_role = request.user.get_role()
                elif hasattr(request.user, 'role'):
                    try:
                        user_role = Role(request.user.role)
                    except (ValueError, TypeError):
                        user_role = None

            if not request.user.is_authenticated or user_role is None:
                return JsonResponse(
                    {
                        'error': 'AUTHENTICATION_REQUIRED',
                        'message': 'Authentication required'
                    },
                    status=401
                )

            if user_role not in roles:
                return JsonResponse(
                    {
                        'error': 'PERMISSION_DENIED',
                        'message': f'Insufficient permissions. Required roles: {[r.name for r in roles]}'
                    },
                    status=403
                )

            return original_dispatch(self, request, *args, **kwargs)

        cls.dispatch = new_dispatch
        return cls

    return decorator


def required_roles(*roles: Role):
    """
    Decorator for function-based views
    """
    def decorator(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            user_role = getattr(request, 'user_role', None)

            if user_role is None:
                if hasattr(request.user, 'get_role'):
                    user_role = request.user.get_role()
                elif hasattr(request.user, 'role'):
                    try:
                        user_role = Role(request.user.role)
                    except (ValueError, TypeError):
                        user_role = None

            if not request.user.is_authenticated or user_role is None:
                return JsonResponse(
                    {
                        'error': 'AUTHENTICATION_REQUIRED',
                        'message': 'Authentication required'
                    },
                    status=401
                )

            if user_role not in roles:
                return JsonResponse(
                    {
                        'error': 'PERMISSION_DENIED',
                        'message': f'Insufficient permissions. Required roles: {[r.name for r in roles]}'
                    },
                    status=403
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
