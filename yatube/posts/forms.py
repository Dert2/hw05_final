from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': 'Группа',
            'text': 'Запись',
            'image': 'Картинка'
        }
        help_texts = {
            'group': 'Выберите название группы',
            'text': 'Напишите что-нибудь'
        }

    def clean_subject(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError("Это поле нужно заполнить!")
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий'
        }
        help_texts = {
            'text': 'Напишите что-нибудь'
        }

    def clean_subject(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError("Это поле нужно заполнить!")
        return text
