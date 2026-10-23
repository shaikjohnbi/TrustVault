

# Create your tests here.

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from audit.models import AuditEvent
from audit.services import record_event
from documents.models import Document


User = get_user_model()


class AuditEventTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="audit_owner",
            password="TestPassword123!",
        )

        self.document = Document.objects.create(
            owner=self.user,
            title="Audit Test Document",
            category="Testing",
            file=SimpleUploadedFile(
                "audit-test.txt",
                b"Audit test content",
                content_type="text/plain",
            ),
        )

    def test_record_successful_upload_event(self):
        event = record_event(
            actor=self.user,
            action="document_upload",
            document=self.document,
        )

        self.assertEqual(event.action, "document_upload")
        self.assertEqual(event.outcome, "success")
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.document, self.document)

    def test_record_denied_access_event(self):
        event = record_event(
            actor=self.user,
            action="document_view",
            outcome="denied",
            document=self.document,
            details={"reason": "permission_denied"},
        )

        self.assertEqual(event.outcome, "denied")
        self.assertEqual(
            event.details["reason"],
            "permission_denied",
        )

    def test_audit_event_without_authenticated_actor(self):
        event = record_event(
            actor=None,
            action="document_view",
            outcome="denied",
        )

        self.assertIsNone(event.actor)
        self.assertEqual(event.outcome, "denied")

    def test_audit_events_are_ordered_newest_first(self):
        older = AuditEvent.objects.create(
            actor=self.user,
            document=self.document,
            action="document_upload",
        )
        newer = AuditEvent.objects.create(
            actor=self.user,
            document=self.document,
            action="document_download",
        )

        events = list(AuditEvent.objects.all())

        self.assertEqual(events[0].id, newer.id)
        self.assertEqual(events[1].id, older.id)

class PermissionAuditRouteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="permission_owner",
            password="TestPassword123!",
        )
        self.viewer = User.objects.create_user(
            username="permission_viewer",
            password="TestPassword123!",
        )

        self.document = Document.objects.create(
            owner=self.owner,
            title="Permission Audit Test",
            category="Testing",
            file=SimpleUploadedFile(
                "permission-test.txt",
                b"Permission audit content",
                content_type="text/plain",
            ),
        )

    def test_grant_permission_creates_audit_event(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            f"/api/documents/{self.document.id}/grants/",
            data={
                "username": self.viewer.username,
                "permission": "read",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            AuditEvent.objects.filter(
                action="permission_grant",
                outcome="success",
                document=self.document,
            ).exists()
        )

    def test_revoke_permission_creates_audit_event(self):
        from documents.models import DocumentGrant

        grant = DocumentGrant.objects.create(
            document=self.document,
            user=self.viewer,
            permission="read",
        )

        self.client.force_login(self.owner)

        response = self.client.delete(
            f"/api/documents/{self.document.id}/grants/?grant_id={grant.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            DocumentGrant.objects.filter(pk=grant.id).exists()
        )
        self.assertTrue(
            AuditEvent.objects.filter(
                action="permission_revoke",
                outcome="success",
                document=self.document,
            ).exists()
        )

class UnauthorizedDownloadAuditTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="download_owner",
            password="TestPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="download_other",
            password="TestPassword123!",
        )

        self.document = Document.objects.create(
            owner=self.owner,
            title="Private Download Audit",
            category="Testing",
            file=SimpleUploadedFile(
                "private-download.txt",
                b"Private content",
                content_type="text/plain",
            ),
        )

    def test_denied_download_creates_audit_event(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            f"/api/documents/{self.document.id}/download/"
        )

        self.assertEqual(response.status_code, 404)

        event = AuditEvent.objects.filter(
            actor=self.other_user,
            document=self.document,
            action="document_download",
            outcome="denied",
        ).first()

        self.assertIsNotNone(event)

