import shutil
import tempfile

from django.core.cache import cache
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
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
        cls.user = User.objects.create_user(username='dert123')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Текст',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовая запись',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def check_post_context(
            self,
            expected_post_text,
            expected_post_pub_date,
            expected_post_author):
        self.assertEqual(expected_post_text, 'Тестовая запись')
        self.assertEqual(expected_post_pub_date, PostsPagesTests.post.pub_date)
        self.assertEqual(expected_post_author, PostsPagesTests.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('index'): 'index.html',
            reverse('group_posts', kwargs={'slug': 'test-slug'}): 'group.html',
            reverse('new_post'): 'new_post.html',
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ): 'new_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        object1 = response.context['page'][0]
        post_text = object1.text
        post_pub_date = object1.pub_date
        post_author = object1.author
        post_image = object1.image
        PostsPagesTests.check_post_context(
            self,
            post_text,
            post_pub_date,
            post_author
        )
        self.assertEqual(post_image, Post.objects.get(id=self.post.id).image)

    def test_group_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'group_posts',
            kwargs={'slug': 'test-slug'}))
        object1 = response.context['posts'][0]
        post_text = object1.text
        post_pub_date = object1.pub_date
        post_author = object1.author
        post_image = object1.image
        object1 = response.context['group']
        group_title = object1.title
        group_description = object1.description
        group_slug = object1.slug
        PostsPagesTests.check_post_context(
            self,
            post_text,
            post_pub_date,
            post_author
        )
        self.assertEqual(group_title, 'Заголовок')
        self.assertEqual(group_description, 'Текст')
        self.assertEqual(group_slug, 'test-slug')
        self.assertEqual(post_image, Post.objects.get(id=self.post.id).image)

    def test_new_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'profile',
            kwargs={'username': self.user.username}
        ))
        profile_user = response.context['user']
        object1 = response.context['page'][0]
        page_post_text = object1.text
        page_post_pub_date = object1.pub_date
        page_post_author = object1.author
        page_post_image = object1.image
        self.assertEqual(profile_user, PostsPagesTests.user)
        PostsPagesTests.check_post_context(
            self,
            page_post_text,
            page_post_pub_date,
            page_post_author
        )
        self.assertEqual(
            page_post_image,
            Post.objects.get(id=self.post.id).image
        )

    def test_post_view_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post_view',
            kwargs={'username': self.user.username, 'post_id': self.post.id}
        ))
        user = response.context['user']
        object1 = response.context['post']
        post_text = object1.text
        post_pub_date = object1.pub_date
        post_author = object1.author
        post_image = object1.image
        self.assertEqual(user, PostsPagesTests.user)
        PostsPagesTests.check_post_context(
            self,
            post_text,
            post_pub_date,
            post_author
        )
        self.assertEqual(post_image, Post.objects.get(id=self.post.id).image)

    def test_post_view_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post_view',
            kwargs={'username': self.user.username, 'post_id': self.post.id}
        ))
        user = response.context['user']
        object1 = response.context['post']
        post_text = object1.text
        post_pub_date = object1.pub_date
        post_author = object1.author
        self.assertEqual(user, PostsPagesTests.user)
        PostsPagesTests.check_post_context(
            self,
            post_text,
            post_pub_date,
            post_author
        )

    def test_new_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        cache_test_post = Post.objects.create(
            text='Cache',
            author=self.user
        )
        response_1 = self.authorized_client.get(reverse('index'))
        page_post_1 = response_1.context['page'][0]
        cache_test_post.delete()
        response_2 = self.authorized_client.get(reverse('index'))
        page_post_2 = response_2.context['page'][0]
        self.assertEqual(page_post_1, page_post_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('index'))
        page_post_3 = response_3.context['page'][0]
        self.assertNotEqual(page_post_1, page_post_3)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='dert123')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for i in range(13):
            cls.post = Post.objects.create(
                text='Тестовая запись',
                author=cls.user
            )

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
