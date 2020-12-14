from rest_framework.test import APITestCase as TestCase

# Create your tests here.

from user.serializers import RegistrationSerializer


class TranslateListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Настройка контекста для теста"""
        mail = 'Username@mail.ru'
        username = 'Username'
        password = 'Password1'
        user = {"mail": mail, "username": username, "password": password}
        serializer = RegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def login(self, mail, password):
        """Авторизация пользователя с именем name и паролем password"""
        resp = self.client.post('/login/', data={'mail': mail, 'password': password})
        return resp

    def translate(self, text, bkrs="True", zhonga="False"):
        resp = self.client.post('/translate/?bkrs=' + bkrs + '&zhonga=' + zhonga, data={'text': text})
        return resp

    def test_correct_translate_bkrs(self):
        """Тестирование запроса на перевод авторизованным пользователем в словарь bkrs"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("那不")
        self.assertEqual(resp.status_code, 200)

    def test_correct_translate_zhonga(self):
        """Тестирование запроса на перевод авторизованным пользователем в словарь zhonga"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("那不")
        self.assertEqual(resp.status_code, 200)
