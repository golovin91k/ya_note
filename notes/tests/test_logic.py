from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {'title': 'Заголовок',
                         'text': 'Текст заметки',
                         'slug': 'slug',
                         }

    def test_user_can_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, 'Текст заметки')

    def test_user_can_create_note_without_slug(self):
        del self.form_data['slug']
        self.auth_client.post(self.url, data=self.form_data)
        url = reverse('notes:detail', args=('zagolovok',))
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestNoteEditDelete(TestCase):

    NOTE_MODIFIED = {'title': 'Измененный заголовок',
                     'text': 'Измененный текст',
                     'slug': 'slug_modified',
                     }

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='slug',
                                       author=cls.author
                                       )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = cls.NOTE_MODIFIED

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_MODIFIED['text'])

    def test_author_can_delete_note(self):
        self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
