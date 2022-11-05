from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_pages_uses_correct_template_and_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:<name> доступен.
        При запросе к имени about:<name> применяется правильный шаблон."""
        pages_names_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:author'): 'about/author.html',
        }

        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
