import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Diary',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text='Тестовый пост из группы Дневник',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.auth_user,
            text='Тестовый комментарий 1',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='New_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)

    def check_context_on_pages_with_paginator(self, response):
        """Метод для проверки контекста на страницах с пагинатором."""
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['page_obj'][0].pub_date,
                         self.post.pub_date)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post.text)
        self.assertEqual(response.context['page_obj'][0].author,
                         self.post.author)
        self.assertEqual(response.context['page_obj'][0].group,
                         self.post.group)
        self.assertEqual(response.context['page_obj'][0].image,
                         self.post.image)

    def test_autorized_user_post_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка для авторизованного пользоателя"""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_anymous_user_post_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
         Проверка для не авторизованного пользоателя"""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_author_post_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон.
        Проверка для автора поста"""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом.
        При создании поста указана группа и картинка.
        Пост появляется на главной странице сайта."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context_on_pages_with_paginator(response)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом.
        При создании поста указана группа и картинка.
        Пост появляется на странице выбранной группы."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})))
        self.check_context_on_pages_with_paginator(response)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом.
        При создании поста указана группа и картинка.
        Пост появляетсяна в профайле автора поста"""
        response = (self.authorized_auth_client.
                    get(reverse('posts:profile',
                        kwargs={'username': self.auth_user.username})))
        self.check_context_on_pages_with_paginator(response)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом.
        Комментарий отображается на странице поста"""
        comment = Comment.objects.first()
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post.pk})))
        self.assertEqual(response.context.get('post').author,
                         self.post.author)
        self.assertEqual(response.context.get('post').text,
                         self.post.text)
        self.assertEqual(response.context.get('post').pub_date,
                         self.post.pub_date)
        self.assertEqual(response.context.get('post').group,
                         self.post.group)
        self.assertEqual(response.context.get('post').image,
                         self.post.image)
        self.assertEqual(comment.text, self.comment.text)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.auth_user)

    def test_post_create_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_auth_client.
                    get(reverse('posts:post_edit',
                        kwargs={'post_id': self.post.pk})))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('is_edit'), True)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_post_with_some_group_not_displayed_on_other_group_page(self):
        """Новый пост не попал в группу, для которой не был предназначен."""
        other_group = Group.objects.create(
            title='Тестовая группа',
            slug='mail',
            description='Тестовое описание',
        )
        other_post = Post.objects.create(
            author=self.auth_user,
            text='Тестовый пост из группы Письма',
            group=other_group
        )
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})))
        self.assertNotIn(response.context['page_obj'][0].text,
                         other_post.text)

    def test_post_with_some_group_displayed_on_profile_page(self):
        """Новый пост с группой попал на страницу profile."""
        response = (self.authorized_auth_client.
                    get(reverse('posts:profile',
                        kwargs={'username': self.auth_user.username})))
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_post_with_some_group_displayed_on_index_page(self):
        """Новый пост с группой попал на страницу index."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_post_with_some_group_displayed_on_group_page(self):
        """Новый пост с группой попал на страницу group."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})))
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_comment_displayed_on_profile_page(self):
        """Новый комментарий попал на страницу поста."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': self.post.pk})))
        self.assertIn('comments', response.context)
        self.assertEqual(response.context['comments'][0].text,
                         self.comment.text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Diary',
            description='Тестовое описание',
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.auth_user,
                text='Тестовый пост c указанной группой' + str(i),
                group=cls.group
            )

    def setUp(self):
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)

    def test_first_page_on_homepage_contains_ten_records(self):
        """Паджинатор выводит на 1 странице index, group, profile 10 записей
        Паджинатор выводит на 2 странице index, group, profile 3 записи"""
        address_data = [reverse('posts:index'),
                        reverse('posts:group_list',
                                kwargs={'slug': self.group.slug}),
                        reverse('posts:profile',
                                kwargs={'username': self.auth_user.username}),
                        ]
        for address in address_data:
            with self.subTest(address=address):
                response = self.authorized_auth_client.get(address)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.authorized_auth_client.get(address,
                                                           {'page': 2})
                self.assertEqual(len(response.context['page_obj']), 3)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse("posts:index"))
        response_first_content = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse("posts:index"))
        response_second_content = response.content
        self.assertEqual(response_first_content, response_second_content)

    def test_cache_second(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse("posts:index"))
        response_first_content = response.content
        Post.objects.all().delete()
        cache.clear()
        response = self.client.get(reverse("posts:index"))
        response_second_content = response.content
        self.assertNotEqual(response_first_content, response_second_content)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(author=cls.auth_user,
                                       text='Тестовый пост 1')

    def setUp(self):
        self.user = User.objects.create_user(username='New_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.other_user = User.objects.create_user(username='Other_user')
        self.authorized_other_client = Client()
        self.authorized_other_client.force_login(self.other_user)

    def test_new_post_displayed_to_followers(self):
        """Новый пост появляется в ленте подписчиков."""
        Follow.objects.create(user=self.user, author=self.auth_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)

    def test_new_post_not_displayed_to_unfollowers(self):
        """Новый пост не появляется в ленте тех, кто не подписан."""
        new_post = Post.objects.create(author=self.user,
                                       text='Тестовый пост 2')
        Follow.objects.create(user=self.other_user, author=self.user)
        response = (self.authorized_other_client.
                    get(reverse('posts:follow_index')))
        self.assertEqual(response.context['page_obj'][0].text, new_post.text)
        self.assertNotIn(response.context['page_obj'][0].text, self.post.text)
