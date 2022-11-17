from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Post, Group, Follow
from ..views import NUM_OUTPUT

User = get_user_model()


class TaskPagesTests(TestCase):
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:posts_home_page'): 'posts/index.html',
            reverse('posts:posts_group_page', kwargs={
                'slug': self.group.slug
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.author.username
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id
            }): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_pages_correct_context(self):
        """Шаблон списка постов сформирован с правильным контекстом."""
        reverse_names_list = [
            reverse('posts:posts_home_page'),
            reverse('posts:posts_group_page', kwargs={
                'slug': self.post.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': self.author.username
            })
        ]
        for reverse_name in reverse_names_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(
                    reverse('posts:posts_home_page')
                )
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object, self.post)
                self.assertEqual(first_object.author.username, (
                    self.author.username
                ))
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(
                    first_object.group.slug, self.post.group.slug
                )
                cache.clear()

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post),
        self.assertEqual(response.context.get('post').author.username, (
            self.author.username
        )),
        self.assertEqual(response.context.get('post').text, (
            self.post.text
        ))

        self.assertEqual(response.context.get('post').group.slug, (
            self.post.group.slug
        ))

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.number_of_posts = 14
        for i in range(1, cls.number_of_posts + 1):
            cls.post = Post.objects.create(
                author=cls.author,
                text='Тестовый пост',
                group=cls.group
            )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_index_first_page_contains_n_records(self):
        """Проверка: количество постов на первой странице равно n. """
        response = self.client.get(reverse('posts:posts_home_page'))
        self.assertEqual(len(response.context['page_obj']), NUM_OUTPUT)

    def test_index_contains_remaining_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(
            reverse('posts:posts_home_page') + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            define_number_of_posts_on_the_second_page(
                NUM_OUTPUT, self.number_of_posts
            )
        )

    def test_group_list_first_page_contains_n_records(self):
        """Проверка: количество постов на первой странице равно 10. """
        response = self.client.get(
            reverse('posts:posts_group_page', kwargs={
                'slug': self.post.group.slug
            })
        )
        self.assertEqual(len(response.context['page_obj']), NUM_OUTPUT)

    def test_group_list_contains_remaining_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(
            reverse('posts:posts_group_page', kwargs={
                'slug': self.post.group.slug
            })
            + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            define_number_of_posts_on_the_second_page(
                NUM_OUTPUT, self.number_of_posts
            )
        )

    def test_profile_first_page_contains_n_records(self):
        """Проверка: количество постов на первой странице равно n. """
        response = self.client.get(
            reverse('posts:profile', kwargs={
                'username': self.author.username
            })
        )
        self.assertEqual(len(response.context['page_obj']), NUM_OUTPUT)

    def test_profile_contains_remaining_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(
            reverse('posts:profile', kwargs={
                'username': self.author.username
            })
            + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            define_number_of_posts_on_the_second_page(
                NUM_OUTPUT, self.number_of_posts
            )
        )


class AdditionalViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-slug-2',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group_1
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_in_home_page(self):
        """Тестовый пост отобразился на главной странице"""
        response = self.client.get(reverse('posts:posts_home_page'))
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object.id, self.post.id)

    def test_post_in_group_page(self):
        """Тестовый пост отобразился на странице группы"""
        response = self.client.get(
            reverse('posts:posts_group_page', kwargs={
                'slug': self.group_1.slug
            })
        )
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object.id, self.post.id)

    def test_post_in_false_group_page(self):
        """Тестовый пост не отобразится на странице сторонней группы"""
        response = self.client.get(
            reverse('posts:posts_group_page', kwargs={
                'slug': self.group_2.slug
            })
        )
        post_object = response.context['page_obj']
        self.assertEqual(len(post_object), 0)

    def test_post_in_profile(self):
        """Тестовый пост отобразился на странице профиля"""
        response = self.client.get(
            reverse('posts:profile', kwargs={
                'username': self.author.username
            })
        )
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object.id, self.post.id)

    def test_index_page_cache(self):
        """Проверка работы кэша"""
        new_post = Post.objects.create(
            author=self.author,
            text='Тестовый пост',
            group=self.group_1
        )
        response = self.client.get(
            reverse('posts:posts_home_page')
        )
        response_1 = response.content
        new_post.delete()
        response = self.client.get(
            reverse('posts:posts_home_page')
        )
        response_2 = response.content
        self.assertEqual(response_1, response_2)
        cache.clear()
        response = self.client.get(
            reverse('posts:posts_home_page')
        )
        response_3 = response.content
        self.assertNotEqual(response_1, response_3)


class FollowUnfollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='just_user')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_unfollow_view(self):
        """
        Авторизованный пользователь может подписываться на других пользователей
        и удалять их из подписок
        """
        following_count = Follow.objects.filter(
            user=self.user
        ).count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.author.username
            })
        )
        new_following_count = Follow.objects.filter(
            user=self.user
        ).count()
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={
                    'username': self.author.username
                }
            )
        )
        self.assertEqual(new_following_count, following_count + 1)
        following_count = new_following_count
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={
                'username': self.author.username
            })
        )
        new_following_count = Follow.objects.filter(
            user=self.user
        ).count()
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={
                    'username': self.author.username
                }
            )
        )
        self.assertEqual(new_following_count, following_count - 1)

    def test_new_following_is_on_the_page(self):
        """
        Посты пользователя появляются в ленте тех, кто на него подписан
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.author.username
            })
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object.id, self.post.id)

    def test_unfollow_is_on_the_page(self):
        """
        Посты пользователя не появляются в ленте тех, кто на него не подписан
        """
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']
        self.assertEqual(len(post_object), 0)

    def test_follow_to_myself_is_false(self):
        """Проверка: нельзя подписыватьcя на самого себя"""
        following_count = self.user.follower.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.user.username
            })
        )
        self.assertEqual(following_count, self.user.follower.count())


def define_number_of_posts_on_the_second_page(
        num_posts: int, total_posts: int
) -> int:
    if total_posts - num_posts >= num_posts:
        return num_posts
    else:
        return total_posts - num_posts
