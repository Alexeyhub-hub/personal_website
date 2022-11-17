from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_urls_uses_correct_template_for_authorized_clients(self):
        """Проверка: корректные шаблоны для авторизованных пользователей"""
        url_names_for_authorized_users = {
            '/create/': 'posts/create_post.html'
        }
        for address, template in url_names_for_authorized_users.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_guest_clients(self):
        """Проверка: корректные шаблоны для анонимных пользователей"""
        url_names_for_all_users = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html'
        }
        for address, template in url_names_for_all_users.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location_for_guest_clients(self):
        """Проверка URL для анонимных пользователей"""
        url_names_for_all_users = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html'
        }
        for address in url_names_for_all_users.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_for_authorized_clients(self):
        """Проверка URL для авторизованных пользователей"""
        url_names_for_authorized_users = {
            '/create/': 'posts/create_post.html'
        }
        for address in url_names_for_authorized_users.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_list_url_redirect_anonymous(self):
        url_names_for_authorized_users = {
            '/create/': 'posts/create_post.html'
        }
        for address in url_names_for_authorized_users.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_add_comment_for_anonymous_users(self):
        """
        Проверяет, что анонимный пользователь не может комментировать посты
        """
        url_names_for_anonymous_user = {
            f'/posts/{self.post.id}/comment/': 'posts/post_detail.html'
        }
        for address in url_names_for_anonymous_user.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next=/posts/{self.post.id}/comment/')

    def test_urls_uses_correct_template_for_author(self):
        """Проверка: правильные шаблоны для автора поста"""
        url_names_for_author = {
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for address, template in url_names_for_author.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location_for_author(self):
        """Проверка URL для автора поста"""
        url_names_for_author = {
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for address in url_names_for_author.keys():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
