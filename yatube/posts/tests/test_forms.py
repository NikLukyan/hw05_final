import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Дневник',
            slug='Diary',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.auth_user,
            text='Тестовый пост 1',
            group=cls.group,
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
        self.authorized_auth_client = Client()
        self.authorized_auth_client.force_login(self.auth_user)
        self.guest_client = Client()
        self.user = User.objects.create_user(username='New_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authenticated_user_post_create(self):
        """Валидная форма создает новую запись Post и сохраняет ее в БД.
        Запись создается вне зависимости от указания группы и картинки."""
        posts_count = Post.objects.count()
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
        form_data = {'text': 'Тестовый пост 2',
                     'group': self.group.id,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)

    def test_guest_user_try_create_post(self):
        """Создание поста только для аутенфицированного пользователя."""
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data={'text': 'Анонимно создаем пост'}
        )
        expected_page = reverse('users:login')
        start_page = reverse('posts:post_create')
        self.assertRedirects(response, f'{expected_page}?next={start_page}')

    def test_authenticated_user_post_edit(self):
        """Валидная форма редактирует запись post_id и сохраняет ее в БД.
        Запись редактируется вне зависимости от указания группы."""
        form_data = ({'text': 'Первично обновленный текст поста',
                      'group': self.group.id},
                     {'text': 'Вторично обновленный текст поста'},)
        for form in form_data:
            with self.subTest(form=form):
                response = self.authorized_auth_client.post(
                    reverse('posts:post_edit',
                            kwargs={'post_id': self.post.pk}),
                    data=form,
                    follow=True
                )
                self.assertRedirects(response,
                                     reverse('posts:post_detail',
                                             kwargs={'post_id': self.post.pk}))
        post = Post.objects.first()
        self.assertEqual(post.text, form_data[1]['text'])

    def test_authenticated_non_author_try_edit_post(self):
        """Страница редактирования поста доступна только для его автора."""
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data={'text': 'Вносим правки в чужой пост'},
        )
        self.assertIsNone(response.context)
        self.assertRedirects(response, '/posts/1/')

    def test_authenticated_user_post_create_with_image(self):
        """При отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных."""
        posts_count = Post.objects.count()
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
        form_data = {'text': 'Тестовый пост 3',
                     'group': self.group.id,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_authenticated_user_add_comment(self):
        """Валидная форма создает новый комментарий и сохраняет его в БД.
        Комментарий создается аутенфицированным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {'post': self.post,
                     'author': self.user,
                     'text': 'Тестовый комментарий 2'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertIn('comments', response.context)
        self.assertEqual(response.context['comments'][1].text,
                         self.comment.text)

    def test_guest_user_try_comment_post(self):
        """Комментировать посты может только аутенфиц. пользователь."""
        form_data = {'post': self.post,
                     'author': self.user,
                     'text': 'Тестовый комментарий 3'}
        response = self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        expected_page = reverse('users:login')
        start_page = reverse('posts:add_comment',
                             kwargs={'post_id': self.post.pk})
        self.assertRedirects(response, f'{expected_page}?next={start_page}')
