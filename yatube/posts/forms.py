from django import forms

from .models import Post, Comment, Follow


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Текст записи'}
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Текст нового поста',
        }
        required = {'group': False, 'text': True}
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'Добавить комментарий'}
        required = {'text': False}
        fields = ['text']

