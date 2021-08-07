import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.form = PostForm()
        cls.authorized_client = Client()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='dert123')
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Текст',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_title_label(self):
        group_label = self.form.fields['group'].label
        text_label = self.form.fields['text'].label
        self.assertEqual(group_label, 'Группа')
        self.assertEqual(text_label, 'Запись')

    def test_title_help_text(self):
        group_help_text = self.form.fields['group'].help_text
        text_help_text = self.form.fields['text'].help_text
        self.assertEqual(group_help_text, 'Выберите название группы')
        self.assertEqual(text_help_text, 'Напишите что-нибудь')

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'author': self.user,
            'image': Post.objects.get(id=self.post.id).image,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=self.user,
                image=Post.objects.get(id=self.post.id).image
            ).exists()
        )

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
            'image': Post.objects.get(id=self.post.id).image
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Измененный текст',
            id=self.post.id,
            image=Post.objects.get(id=self.post.id).image
        ).exists())
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_client_cant_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertFalse(Post.objects.filter(
            text='Измененный текст',
            id=self.post.id
        ).exists())
        self.assertEqual(Post.objects.count(), post_count)
