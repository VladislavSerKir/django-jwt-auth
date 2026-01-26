from functools import wraps
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import AnonymousUser
from typing import Optional
from rest_framework import status


from apps.users.enums import Role


class RBACMiddleware:
    """
    Middleware for role-based access control that works AFTER DRF authentication
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        return response

    def _get_user_role(self, request: HttpRequest) -> Optional[Role]:
        """Get user role"""
        if not hasattr(request, 'user') or not request.user:
            return None

        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            return None

        try:
            if hasattr(request.user, 'get_role'):
                return request.user.get_role()
            elif hasattr(request.user, 'role'):
                return Role(request.user.role)
        except Exception as e:
            print(f"Error getting user role: {e}")

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called before view function execution
        But we need to wait for DRF to authenticate
        """
        request.user_role = self._get_user_role(request)

        return None

    def _check_permissions(self, request, required_roles):
        """Check if user has required roles"""
        if not hasattr(request, 'user') or not request.user or not request.user.is_authenticated:
            return JsonResponse(
                {
                    'error': 'AUTHENTICATION_REQUIRED',
                    'message': 'Authentication required'
                },
                status=401
            )

        user_role = getattr(request, 'user_role', None)
        print(f"ROLES {user_role} in {required_roles}")

        if user_role is None or user_role not in required_roles:
            return JsonResponse(
                {
                    'error': 'PERMISSION_DENIED',
                    'message': f'Insufficient permissions. Required roles: {[r.name for r in required_roles]}'
                },
                status=403
            )

        return None


def with_roles(*roles: Role):
    """
    Decorator for setting required roles at function/class level
    Fixed version - preserves class as class
    """
    def decorator(obj):
        if callable(obj):
            if isinstance(obj, type):
                obj.required_roles = roles
                return obj
            elif hasattr(obj, '__name__') and not hasattr(obj, '__call__'):
                obj.required_roles = roles
                return obj
            else:
                if hasattr(obj, '__self__'):
                    obj.required_roles = roles
                    return obj
                else:
                    @wraps(obj)
                    def wrapper(*args, **kwargs):
                        return obj(*args, **kwargs)
                    wrapper.required_roles = roles
                    return wrapper
        else:
            obj.required_roles = roles
            return obj

    return decorator


def require_roles(*required_roles):
    """
    Decorator for APIView methods that checks roles AFTER DRF authentication
    """
    def decorator(view_method):
        @wraps(view_method)
        def wrapped_view(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse(
                    {
                        'error': 'AUTHENTICATION_REQUIRED',
                        'message': 'Authentication required'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user_role = None
            if hasattr(request.user, 'get_role'):
                user_role = request.user.get_role()
            elif hasattr(request.user, 'role'):
                try:
                    user_role = Role(request.user.role)
                except (ValueError, TypeError):
                    user_role = None

            if user_role is None or user_role not in required_roles:
                return JsonResponse(
                    {
                        'error': 'PERMISSION_DENIED',
                        'message': f'Insufficient permissions. Required roles: {[r.name for r in required_roles]}'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_method(self, request, *args, **kwargs)

        return wrapped_view
    return decorator
