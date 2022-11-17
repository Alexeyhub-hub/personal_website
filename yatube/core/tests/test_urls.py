from django.test import TestCase


class CustomURLTests(TestCase):
    """Проверка: ошибка 404 вызывает правильный шаблон"""
    def test_404_page_call_certain_template(self):
        response = self.client.get('/something_really_weird')
        self.assertTemplateUsed(response, 'core/404.html')
