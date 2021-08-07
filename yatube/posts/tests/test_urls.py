from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_uses_correct_template(self):
        response = self.guest_client.get('')
        self.assertTemplateUsed(response, 'index.html')


class GroupAndPostURLTests(TestCase):
    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Post_Author')
        self.user1 = User.objects.create_user(username='Not_Post_Author')
        self.authorized_client = Client()
        self.authorized_not_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_not_author.force_login(self.user1)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        self.post = Post.objects.create(
            text='Тестовая запись',
            group=self.group,
            author=self.user
        )

    def test_new_post_url(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_redirect_anonymous(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_post_url_redirect_anonymous(self):
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_url(self):
        response = self.guest_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_view_url(self):
        response = self.guest_client.get(reverse(
            'post_view',
            kwargs={'username': self.user.username, 'post_id': self.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_anonymous(self):
        response = self.guest_client.get(
            f'/{self.user.username}/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_post_author(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_for_not_author(self):
        response = self.authorized_not_author.get(
            f'/{self.post.author}/{self.post.id}/edit'
        )
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_urls_use_correct_template(self):
        templates_url_names = {
            '/group/test-slug/': 'group.html',
            '/new/': 'new_post.html',
            f'/{self.user.username}/{self.post.id}/edit/': 'new_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(template=template, url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_return_404(self):
        response = self.guest_client.get('/wrongname')
        self.assertTrue(response.status_code, HTTPStatus.NOT_FOUND)
