from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class ModelStrTest(TestCase):
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
            text='4' * 20,
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает метод __str__."""
        test_post = ModelStrTest.post
        test_group = ModelStrTest.group
        expected_post_name = test_post.text[:settings.MAX_POST_STR]
        expected_group_name = test_group.title
        self.assertEqual(expected_post_name, str(test_post),
                         ('У модели Post некорректно'
                          'работает метод __str__.'))
        self.assertEqual(expected_group_name, str(test_group),
                         ('У модели Group некорректно'
                          'работает метод __str__.'))


class PostModelFieldsTest(TestCase):
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
            text='Тект тестового поста',
            group=cls.group
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task = PostModelFieldsTest.post
        field_verboses = {
            'author': 'Автор',
            'text': 'Текст поста',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = PostModelFieldsTest.post
        field_help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Введите текст поста',
            'image': 'Загрузите картинку',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expected_value)
