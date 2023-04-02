from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()

NUM_CHARACTERS: int = 15


class Category(CreatedModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ['slug', ]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Post(CreatedModel):
    title = models.CharField(max_length=255)
    text = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        null=True,
        related_name='posts'
    )
    description = models.TextField(null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='projects/',
        blank=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:NUM_CHARACTERS]
