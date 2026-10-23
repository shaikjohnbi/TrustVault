

# Create your tests here.

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Document, DocumentGrant
from .permissions import can_access_document


User = get_user_model()


class DocumentPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="TestPassword123!",
        )
        self.viewer = User.objects.create_user(
            username="viewer",
            password="TestPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="TestPassword123!",
        )

        self.document = Document.objects.create(
            owner=self.owner,
            title="Private Test Document",
            category="Testing",
            description="Security test document",
            file=SimpleUploadedFile(
                "private-test.txt",
                b"Private document content",
                content_type="text/plain",
            ),
        )
        
    def test_ungranted_user_cannot_edit_document(self):
        self.client.force_login(self.other_user)
        response = self.client.patch(
            f"/api/documents/{self.document.id}/",
            data='{"title": "Hacked Title"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, "Private Test Document")

    def test_ungranted_user_cannot_delete_document(self):
        self.client.force_login(self.other_user)
        response = self.client.delete(
            f"/api/documents/{self.document.id}/"
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Document.objects.filter(pk=self.document.id).exists()
        )

    def test_non_owner_cannot_manage_document_grants(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            f"/api/documents/{self.document.id}/grants/",
            data='{"username": "viewer", "permission": "read"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            DocumentGrant.objects.filter(
                document=self.document,
                user=self.viewer,
            ).exists()
        )
        
    def test_upload_rejects_empty_file(self):
        self.client.force_login(self.owner)

        empty_file = SimpleUploadedFile(
            "empty.txt",
            b"",
            content_type="text/plain",
        )

        response = self.client.post(
            "/api/documents/upload/",
            {
                "title": "Empty File",
                "file": empty_file,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_upload_rejects_unsupported_extension(self):
        self.client.force_login(self.owner)

        invalid_file = SimpleUploadedFile(
            "malicious.exe",
            b"sample content",
            content_type="application/octet-stream",
        )

        response = self.client.post(
            "/api/documents/upload/",
            {
                "title": "Unsupported File",
                "file": invalid_file,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_upload_rejects_corrupted_image(self):
        self.client.force_login(self.owner)

        corrupted_image = SimpleUploadedFile(
            "broken.png",
            b"this is not a real image",
            content_type="image/png",
        )

        response = self.client.post(
            "/api/documents/upload/",
            {
                "title": "Broken Image",
                "file": corrupted_image,
            },
        )

        self.assertEqual(response.status_code, 400)
    
    def test_revoked_user_cannot_download_document(self):
        grant = DocumentGrant.objects.create(
            document=self.document,
            user=self.viewer,
            permission=DocumentGrant.Permission.READ,
        )

        self.client.force_login(self.viewer)

        # User can download before permission is revoked.
        response_before = self.client.get(
            f"/api/documents/{self.document.id}/download/"
        )
        self.assertEqual(response_before.status_code, 200)

        # Revoke permission.
        grant.delete()

        # The very next request must be denied.
        response_after = self.client.get(
            f"/api/documents/{self.document.id}/download/"
        )
        self.assertEqual(response_after.status_code, 404)



    def test_owner_can_access_document(self):
        self.assertTrue(
            can_access_document(self.owner, self.document, "read")
        )
        self.assertTrue(
            can_access_document(self.owner, self.document, "edit")
        )

    def test_ungranted_user_cannot_access_document(self):
        self.assertFalse(
            can_access_document(self.other_user, self.document, "read")
        )
        self.assertFalse(
            can_access_document(self.other_user, self.document, "edit")
        )

    def test_read_grant_cannot_edit_document(self):
        DocumentGrant.objects.create(
            document=self.document,
            user=self.viewer,
            permission=DocumentGrant.Permission.READ,
        )

        self.assertTrue(
            can_access_document(self.viewer, self.document, "read")
        )
        self.assertFalse(
            can_access_document(self.viewer, self.document, "edit")
        )

    def test_edit_grant_allows_read_and_edit(self):
        DocumentGrant.objects.create(
            document=self.document,
            user=self.viewer,
            permission=DocumentGrant.Permission.EDIT,
        )

        self.assertTrue(
            can_access_document(self.viewer, self.document, "read")
        )
        self.assertTrue(
            can_access_document(self.viewer, self.document, "edit")
        )

    def test_revoked_grant_removes_access_immediately(self):
        grant = DocumentGrant.objects.create(
            document=self.document,
            user=self.viewer,
            permission=DocumentGrant.Permission.READ,
        )

        self.assertTrue(
            can_access_document(self.viewer, self.document, "read")
        )

        grant.delete()

        self.assertFalse(
            can_access_document(self.viewer, self.document, "read")
        )

    def test_document_detail_denies_ungranted_user(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            f"/api/documents/{self.document.id}/"
        )

        self.assertEqual(response.status_code, 403)

    
    def test_download_denies_ungranted_user(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            f"/api/documents/{self.document.id}/download/"
        )

        self.assertEqual(response.status_code, 404)
    
    
