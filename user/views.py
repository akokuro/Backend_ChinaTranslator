from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotAuthenticated, ValidationError

from django.db.utils import IntegrityError

from .models import MyUser
from .backends import JWTAuthentication
from .serializers import LoginSerializer
from .serializers import RegistrationSerializer


def custom_exception_handler(exc, context):
    """Реагирует на исключение
    Если исключение NotAuthenticated(неавторизованный запрос), возвращает 401
    Если  IntegrityError(попытка регистрации под существующим username), возвращает 403
    Если ValidationError(неудачная попытка логина), возвращает 403"""
    if isinstance(exc, NotAuthenticated):
        return Response(str(exc), status=status.HTTP_401_UNAUTHORIZED)
    if isinstance(exc, IntegrityError):
        return Response(str(exc), status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, ValidationError):
        return Response(str(exc), status=status.HTTP_403_FORBIDDEN)
    response = exception_handler(exc, context)
    return response


class RegistrationAPIView(APIView):
    """ Регистрация нового пользователя 
    Доступен всем пользователям"""
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def register_user(self, mail, username, password):
        """Регистрация пользователя с именем username и паролем password
        Возвращает сериализатор пользователя"""
        user = {"mail": mail, "username": username, "password": password}
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    def post(self, request):
        """Обработка post-запроса 
        Регистрирует пользователя из данных полученного json и вохвращает в json токен
        """
        serializer = self.register_user(request.data.get("mail"), request.data.get("username"),
                                        request.data.get("password"))
        response = Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie("Token", serializer.data.get("token", None))
        return response


class LoginAPIView(APIView):
    """ Авторизация пользователя 
    Доступен всем пользователям"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """Обработка post-запроса
        Проверяет наличие пользователя с переданными в json данными
        Если такой пользователь сущетсвует, то возвращает json с токеном"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie("Token", serializer.data.get("token", None))
        return response

class GetUserNameAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Обработка post-запроса
        Проверяет наличие пользователя с переданными в json данными
        Если такой пользователь сущетсвует, то возвращает json с токеном"""
        user, _ = JWTAuthentication().authenticate(request)
        return Response(user.username, 200)
