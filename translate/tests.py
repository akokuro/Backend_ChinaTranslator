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

    def test_authenticate_translate_bkrs(self):
        """Тестирование запроса на перевод авторизованным пользователем в словарь bkrs"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("那不")
        self.assertEqual(resp.status_code, 200)

    def test_authenticate_translate_zhonga(self):
        """Тестирование запроса на перевод авторизованным пользователем в словарь zhonga"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("那不", "False", "True")
        self.assertEqual(resp.status_code, 200)

    def test_authenticate_translate(self):
        """Тестирование запроса на перевод авторизованным пользователем в оба словаря"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("那不", "True", "True")
        self.assertEqual(resp.status_code, 200)

    def test_not_authenticate_translate_bkrs(self):
        """Тестирование запроса на перевод не авторизованным пользователем в словарь bkrs"""
        resp = self.translate("那不")
        self.assertEqual(resp.status_code, 401)

    def test_not_authenticate_translate_zhonga(self):
        """Тестирование запроса на перевод не авторизованным пользователем в словарь zhonga"""
        resp = self.translate("那不", "False", "True")
        self.assertEqual(resp.status_code, 401)

    def test_not_authenticate_translate(self):
        """Тестирование запроса на перевод не авторизованным пользователем в оба словаря"""
        resp = self.translate("那不", "True", "True")
        self.assertEqual(resp.status_code, 401)

    def test_authenticate_translate_with_incorrect_text(self):
        """Тестирование запроса на перевод авторизованным пользователем в словарях с некорректным текстом"""
        resp = self.login('Username@mail.ru', 'Password1')
        self.client.raise_request_exception = True

        # длина текста больше 100 символов в словарь bkrs
        resp = self.translate(
            "那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那"
            "不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那"
            "不那不那不那不那不那不那不那不那不那不那不那不那不那不那不")
        self.assertEqual(resp.status_code, 400)

        # длина текста больше 100 символов в словарь zhonga
        resp = self.translate(
            "那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那"
            "不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那"
            "不那不那不那不那不那不那不那不那不那不那不那不那不那不那不", "False", "True")
        self.assertEqual(resp.status_code, 400)

        # длина текста больше 100 символов в оба словаря
        resp = self.translate(
            "那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那"
            "不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那不那"
            "不那不那不那不那不那不那不那不那不那不那不那不那不那不那不", "True", "True")
        self.assertEqual(resp.status_code, 400)

        # текст на отличном от китайского языке словарь bkrs
        resp = self.translate(
            "Русский язык")
        self.assertEqual(resp.status_code, 400)

        # текст на отличном от китайского языке словарь zhonga
        resp = self.translate(
            "Русский язык", "False", "True")
        self.assertEqual(resp.status_code, 400)

        # текст на отличном от китайского языке в оба словаря
        resp = self.translate(
            "Русский язык", "True", "True")
        self.assertEqual(resp.status_code, 400)

        # длина текста меньше одного символа словарь bkrs
        resp = self.translate(
            "Русский язык")
        self.assertEqual(resp.status_code, 400)

        # длина текста меньше одного символа словарь zhonga
        resp = self.translate(
            "Русский язык", "False", "True")
        self.assertEqual(resp.status_code, 400)

        # длина текста меньше одного символа в оба словаря
        resp = self.translate(
            "", "True", "True")
        self.assertEqual(resp.status_code, 400)

    def test_authenticate_translate_text_bkrs(self):
        """Тестирование запроса на перевод авторизованным пользователем в bkrs с проверкой текстаы"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("哪儿")
        self.assertEqual(resp.json()['bkrs'], [['哪儿'], ['nǎr'], ['разг. где?, куда? (вм. 哪里 кроме 5)']])

    def test_authenticate_translate_text_zhonga(self):
        """Тестирование запроса на перевод авторизованным пользователем в zhonga с проверкой текстаы"""
        resp = self.login('Username@mail.ru', 'Password1')
        resp = self.translate("哪儿", "False", "True")
        self.assertEqual(resp.json()['zhonga'], [['哪儿'], ['nǎr'], ['где?, куда? \n\n\nсм. 哪里  \n\n\nгде? где уж там! (вопр)']])
