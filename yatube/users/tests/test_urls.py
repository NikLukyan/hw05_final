from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post, User

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Diary',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.templates_url_names = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_autorized_user_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверяем авторизованного пользователя."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template,
                                        ('Ошибка адреса и шаблона'))

    def test_guest_user_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверяем неавторизированного пользователя."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_user_logout_url_exists_at_desired_location(self):
        """Страница /auth/logout/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_signup_url_exists_at_desired_location(self):
        """Страница /auth/signup/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_login_url_exists_at_desired_location(self):
        """Страница /auth/login/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_password_reset_url_exists_at_desired_location(self):
        """Страница /auth/password_reset/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_password_res_done_url_exists_at_desired_location(self):
        """Страница /auth/password_reset/done/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_reset_done_url_exists_at_desired_location(self):
        """Страница /auth/reset/done/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_autenficated_user_password_change_exists_at_location(self):
        """Страница /password_change/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_autenficated_user_pas_change_done_exists_at_location(self):
        """Страница /password_change/done/ доступна авториз. пользователю"""
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_redirect_anonymous_on_admin_login(self):
        """Страница смены пароля перенаправит анонимного
        пользователя на страницу авторизации.
        """
        response = self.guest_client.get(
            '/auth/password_change/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/')

    def test_password_change_done_url_redirect_anonymous_on_admin_login(self):
        """Страница подтверждения смены пароля перенаправит анонимного
        пользователя на страницу авторизации.
        """
        response = self.guest_client.get(
            '/auth/password_change/done/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/done/')
