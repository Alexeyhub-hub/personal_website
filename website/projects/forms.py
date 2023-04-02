from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {'text': 'Текст записи'}
        help_texts = {
            'text': 'Текст нового поста',
        }
        required = {'text': True}
        fields = ['text', 'image']


