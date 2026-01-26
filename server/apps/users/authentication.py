from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.utils.translation import gettext_lazy as _


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication with blacklist"""

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)

            self._check_blacklist(validated_token)

            return self.get_user(validated_token), validated_token

        except TokenError as e:
            raise InvalidToken({
                'detail': 'Given token not valid for any token type',
                'code': 'token_not_valid',
                'messages': [{
                    'token_class': 'AccessToken',
                    'token_type': 'access',
                    'message': str(e)
                }]
            })

    def _check_blacklist(self, validated_token):
        """Check JWT in blacklist"""
        jti = validated_token.get('jti')

        if jti:
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise InvalidToken(_('Token is blacklisted'))
