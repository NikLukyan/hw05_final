from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User

User = get_user_model()


class UserFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_user_create_form_and_attributes(self):
        """Валидная форма создает нового пользователя и сохраняет его в БД.
        Проверяем переданные атрибуты"""
        last_user = User.objects.last()
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'ivanov',
            'email': 'nikluk@mail.ru',
            'password1': 'ivan1234',
            'password2': 'ivan1234',
        }
        self.guest_client.post(
            reverse('users:signup'), data=form_data, follow=True
        )
        last_user = User.objects.last()
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(last_user.username, form_data['username'])
        self.assertEqual(last_user.email, form_data['email'])
        self.assertEqual(last_user.first_name, form_data['first_name'])
        self.assertEqual(last_user.last_name, form_data['last_name'])
