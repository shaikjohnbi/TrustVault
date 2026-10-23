
# Register your models here.


from django.contrib import admin
from .models import Document, DocumentGrant


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "category",
        "created_at",
        "updated_at",
    )

    list_filter = ("category", "created_at")

    search_fields = (
        "title",
        "owner__username",
        "category",
        "description",
    )

    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(DocumentGrant)
class DocumentGrantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "user",
        "permission",
        "created_at",
    )

    list_filter = ("permission", "created_at")

    search_fields = (
        "document__title",
        "user__username",
        "document__owner__username",
    )

    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
