from functools import wraps
from django.http import JsonResponse
from rest_framework import status


from apps.users.enums import Role


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
