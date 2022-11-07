from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Diary',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='New_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)
        cache.clear()

    def test_guest_user_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка для неавторизованного пользователя."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_autenficated_user_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка для авторизованного пользователя."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_author_user_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка для автора поста."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_auth_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_user_url_exists_at_desired_location(self):
        """Проверка доступности страниц для неавторизованного пользователя."""
        address_data = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        )
        for address in address_data:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_url_exists_at_desired_location(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        address_data = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
            '/create/',
        )
        for address in address_data:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_url_exists_at_desired_location(self):
        """Проверка доступности страниц для автора поста."""
        address_data = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
            '/create/',
            f'/posts/{self.post.pk}/edit/',
        )
        for address in address_data:
            with self.subTest(address=address):
                response = self.authorized_auth_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_try_unexisting_page_and_get_error(self):
        """Запрос к несуществующей странице вернёт ошибку 404.
        Cтраница 404 отдаёт кастомный шаблон"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница редактирования поста перенаправит анонимного
        пользователя на страницу авторизации.
        """
        response = self.guest_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_edit_url_redirect_autenficated_on_post_detail(self):
        """Страница редактирования поста перенаправит авторизованного
        пользователя на страницу поста без возможности редактирования.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.pk}/')


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text='Тестовый пост 1',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='New_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_autorized_user_try_following_to_author(self):
        """Авторизованный user может подписываться на других авторов.
        Авторизованный user может удалять авторов из подписок."""
        follow_count = Follow.objects.count()
        follow_response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.auth_user.username},
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertRedirects(
            follow_response, f'/profile/{self.auth_user.username}/'
        )
        unfollow_response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.auth_user.username},
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertRedirects(unfollow_response, '/follow/')
