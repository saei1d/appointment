from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class PhoneAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.model.object.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')
        return token.user, token
