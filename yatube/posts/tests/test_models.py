from posts.models import Post, Group

from django.test import TestCase, Client

from django.contrib.auth import get_user_model

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='11111111111111111111',
            author=self.user,
        )

    def test_object_name_is_title_field(self):
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))


class GroupModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )

    def test_object_name_is_title_field(self):
        group = self.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
