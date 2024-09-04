from django.test import Client, TestCase

from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNotesLogic(TestCase):
    TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.anonymous_user = User.objects.create(username='Джон')
        cls.authenticated_user = User.objects.create(username='Тирион')
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.authenticated_user)
        cls.form_data = {'text': cls.TEXT}

    def test_notes_anonymous_user(self):
        response = self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_notes_authenticated_user(self):
        Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='tirion_note',
            author=self.authenticated_user
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_notes_duplicate_slug(self):
        Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='tirion_note',
            author=self.authenticated_user
        )
        with self.assertRaises(Exception):
            Note.objects.create(
                title='Заголовок2',
                text='Текст',
                slug='tirion_note',
                author=self.authenticated_user
            )

    def test_slugify_generates_correct_slug(self):
        title = 'тест'
        expected_slug = 'test'
        generated_slug = slugify(title)
        self.assertEqual(generated_slug, expected_slug)


class TestEditDeleteNotes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_frodo = User.objects.create(username='Фродо')
        cls.user_sam = User.objects.create(username='Сэм')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user_frodo)
        cls.note = Note.objects.create(
            title='Заголовок_Фродо',
            text='Текст_Фродо',
            slug='frodo_note',
            author=cls.user_frodo
        )
        cls.form_data = {'title': 'Проверка', 'text': 'Текст'}
        cls.url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_edit_suer_frodo(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Проверка')

    def test_edit_user_sam(self):
        self.client.force_login(self.user_sam)
        response = self.client.post(self.edit, self.form_data)
        self.assertNotEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, 'Проверка')

    def test_delete_user_frodo(self):
        self.auth_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_delete_user_sam(self):
        self.client.force_login(self.user_sam)
        self.client.delete(self.delete_url)
        note_count = Note.objects.count()
        self.assertNotEqual(note_count, 0)
