
# Create your models here.
from django.conf import settings
from django.db import models


class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_documents",
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="private_documents/")
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DocumentGrant(models.Model):
    class Permission(models.TextChoices):
        READ = "read", "Read"
        EDIT = "edit", "Edit"

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="grants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_grants",
    )
    permission = models.CharField(
        max_length=10,
        choices=Permission.choices,
        default=Permission.READ,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["document", "user"],
                name="unique_document_user_grant",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.document} ({self.permission})"
