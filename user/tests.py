from rest_framework.test import APITestCase as TestCase

from .models import MyUser as User

# Create your tests here.

from .serializers import RegistrationSerializer


class UserListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Настройка контекста для теста"""
        number_of_users = 5
        for user_num in range(number_of_users):
            mail = 'Username%s' % user_num + "@mail.ru"
            username = 'Username%s' % user_num
            password = 'Password%s' % user_num
            user = {"mail": mail, "username": username, "password": password}
            serializer = RegistrationSerializer(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def signup(self, mail, username, password):
        """Регистрация пользователя с именем name и паролем password"""
        resp = self.client.post('/register/', data={'mail': mail, 'username': username, 'password': password})
        return resp

    def login(self, mail, password):
        """Авторизация пользователя с именем name и паролем password"""
        resp = self.client.post('/login/', data={'mail': mail, 'password': password})
        return resp

    def test_correct_signup(self):
        """Тестирование регистрации пользователя с корректными данными"""
        resp = self.signup('Username6@mail.ru', 'Username6', 'Password6')
        self.assertEqual(resp.status_code, 201)

    def test_correct_login(self):
        """Тестирование авторизации пользователя с корректными данными"""
        resp = self.login('Username4@mail.ru', 'Password4')
        self.assertEqual(resp.status_code, 200)

    def test_incorrect_login(self):
        """Тестирование автризации несуществущего пользователя"""
        resp = self.login('Username7@mail.ru', 'Password7')
        self.assertEqual(resp.status_code, 401)

    def test_signup_with_exists_username(self):
        """Тестирование регистрации существующего пользователя"""
        resp = self.signup('Username4@mail.ru', 'Username4', 'Password4')
        self.assertEqual(resp.status_code, 403)

    def test_signup_with_incorrect_credentials(self):
        """Тестирование регистрации пользователя с несоответствующими шаблону данными"""
        self.client.raise_request_exception = True
        # Пароль больше 12 символов
        resp = self.signup('Username7@mail.ru', 'Username7', 'Password638753893101')
        self.assertEqual(resp.status_code, 401)
        # Пароль меньше 6 символов
        resp = self.signup('Username41@mail.ru', 'Username7', 'Pass')
        self.assertEqual(resp.status_code, 401)
        # Пароль состоит не только из английских букв и цифр
        resp = self.signup('Username7@mail.ru', 'Username7', 'Password6!')
        self.assertEqual(resp.status_code, 201)
