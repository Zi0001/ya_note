from django.test import TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestHomePage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user_tom = User.objects.create(username='Томас')
        cls.user_katrin = User.objects.create(username='Катрин')

        cls.note_tom = Note.objects.create(
            title='Заметка Тома',
            text='Текст Тома',
            slug='note_tom',
            author=cls.user_tom
        )
        cls.note_katrin = Note.objects.create(
            title='Заметка Катрин',
            text='Текст Катрин',
            slug='note_katrin',
            author=cls.user_katrin
        )

    def test_list_notes(self):
        self.client.force_login(self.user_tom)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)

    def test_notes_unique(self):
        self.client.force_login(self.user_tom)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)
        self.assertEqual(object_list.count(), 1)
        self.assertEqual(object_list.first().author, self.user_tom)
        self.client.force_login(self.user_katrin)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIsNotNone(object_list)
        self.assertEqual(object_list.count(), 1)
        self.assertEqual(object_list.first().author, self.user_katrin)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.user_tom)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_tom.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
