from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.anonymous_user = User.objects.create(username='Тим')
        cls.authenticated_user = User.objects.create(username='Нео')

        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='record1',
            author=cls.authenticated_user
        )

    '''Задание 1_1'''
    def test_anonimous(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    '''Задание 1_2'''
    def test_authenticated(self):
        self.client.force_login(self.authenticated_user)
        for name in ('notes:home', 'notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    '''Задание 1_3'''
    def test_pages_access(self):
        users_statuses = (
            (self.authenticated_user, HTTPStatus.OK),
            (self.anonymous_user, HTTPStatus.NOT_FOUND),
        )
  
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:detail', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous(self):
        login_url = reverse('users:login')
        urls = ( 
            ('notes:add', None), 
            ('notes:edit', (self.notes.slug,)), 
            ('notes:detail', (self.notes.slug,)), 
            ('notes:delete', (self.notes.slug,)), 
            ('notes:list', None), 
            ('notes:success', None)
        ) 

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_static_pages(self):
        users_statuses = (
            (self.authenticated_user, HTTPStatus.OK),  
            (self.anonymous_user, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('users:login', 'users:logout'):
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

