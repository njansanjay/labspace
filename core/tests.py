from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import check_password
from core.models import Space, Note, SpaceFile

class LabSpaceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.space_id = "testroom123"
        self.password = "secretpass123"
        self.space = Space.objects.create(
            space_id=self.space_id,
            password=Space.objects.make_password if hasattr(Space.objects, 'make_password') else "pbkdf2_sha256$test"
        )
        # Re-set hashed password properly
        from django.contrib.auth.hashers import make_password
        self.space.password = make_password(self.password)
        self.space.save()

    def test_create_space(self):
        new_space_id = "newroom99"
        response = self.client.post(reverse("create_space"), {
            "space_id": new_space_id,
            "password": "mypassword123",
            "confirm_password": "mypassword123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Space.objects.filter(space_id=new_space_id).exists())
        space = Space.objects.get(space_id=new_space_id)
        self.assertTrue(check_password("mypassword123", space.password))

    def test_open_space_correct_password(self):
        response = self.client.post(reverse("open_space"), {
            "space_id": self.space_id,
            "password": self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("space_id"), self.space_id)

    def test_open_space_wrong_password(self):
        response = self.client.post(reverse("open_space"), {
            "space_id": self.space_id,
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.client.session.get("space_id"), self.space_id)

    def test_add_and_delete_note(self):
        # First unlock session
        session = self.client.session
        session["space_id"] = self.space_id
        session.save()

        # Add note
        response = self.client.post(reverse("add_note", kwargs={"space_id": self.space_id}), {
            "title": "Test Title",
            "content": "This is a test note content."
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.filter(space=self.space).count(), 1)

        note = Note.objects.get(space=self.space)
        self.assertEqual(note.title, "Test Title")
        self.assertEqual(note.content, "This is a test note content.")

        # Delete note
        response = self.client.get(reverse("delete_note", kwargs={"space_id": self.space_id, "note_id": note.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.filter(space=self.space).count(), 0)

    def test_upload_and_delete_file(self):
        # Set session
        session = self.client.session
        session["space_id"] = self.space_id
        session.save()

        uploaded_file = SimpleUploadedFile("sample.txt", b"Hello LabSpace storage!", content_type="text/plain")
        response = self.client.post(reverse("upload_file", kwargs={"space_id": self.space_id}), {
            "file": uploaded_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SpaceFile.objects.filter(space=self.space).count(), 1)

        space_file = SpaceFile.objects.get(space=self.space)
        self.assertEqual(space_file.filename, "sample.txt")
        self.assertEqual(space_file.file_type, "text")

        # Delete file
        response = self.client.get(reverse("delete_file", kwargs={"space_id": self.space_id, "file_id": space_file.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SpaceFile.objects.filter(space=self.space).count(), 0)
