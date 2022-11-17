import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_form(self):
        """При отправке формы создается новая запись поста"""
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
        form_data = {
            'text': 'Второй тестовый пост',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        address = Post.objects.get(
            text='Второй тестовый пост'
        ).image
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id,
                image=address
            ).exists()
        )

    def test_create_comment_form(self):
        """При отправке формы создается новая запись комментария"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Просто комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_index_image_shown_correct(self):
        """
        при выводе поста с картинкой изображение передаётся в словаре context
        """
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
        form_data = {
            'text': 'Второй тестовый пост',
            'group': self.group.id,
            'image': uploaded,
        }
        new_post = Post.objects.create(
            text='новый пост',
            author=self.author,
            group=self.group,
            image=uploaded
        )
        reverse_names_sheet = [
            reverse('posts:posts_home_page'),
            reverse('posts:posts_group_page', kwargs={
                'slug': self.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': self.author.username
            }),
        ]
        for reverse_name in reverse_names_sheet:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name,
                    data=form_data,
                    follow=True
                )
                context = (
                    response.context.get('page_obj')[0]
                )
                self.assertEqual(context.image, new_post.image)
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': new_post.id
            }),
            data=form_data,
            follow=True
        )
        context = (
            response.context.get('post')
        )
        self.assertEqual(context.image, new_post.image)

    def test_edit_post_form(self):
        """При отправке формы редактирования происходит изменение поста"""
        new_group = Group.objects.create(
            title='Вторая группа',
            slug='2-slug',
            description='Просто описание',
        )
        form_data = {
            'text': 'Измененный пост',
            'group': new_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group.id, new_group.id)
