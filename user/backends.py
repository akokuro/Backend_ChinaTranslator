import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import MyUser


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """
        request.user = None

        token = self.get_token_from_headers(request)
        if token == None:
            token = self.get_token_from_cookie(request)
        if token == None:
            return None
        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def get_token_from_headers(self, request):
        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Token") and 2) the JWT
    # that we should authenticate against.

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()


        if not auth_header or len(auth_header) != 2:
            # Invalid token header. The Token string should not contain spaces.
            # Do not attempt to authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None
        return token


    def get_token_from_cookie(self, request):
        """
        Пытается получить токен из кук, возвращает токен или None
        """
        token = None
        if self.authentication_header_prefix in request.COOKIES:
            token = request.COOKIES[self.authentication_header_prefix]
        return token

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        print(token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            print(msg)
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = MyUser.objects.get(pk=payload['id'])
        except MyUser.DoesNotExist:
            msg = 'No user matching this token was found.'
            print(msg)
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            print(msg)
            raise exceptions.AuthenticationFailed(msg)
        print("ok")
        return (user, token)
