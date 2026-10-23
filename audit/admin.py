
# Register your models here.


from django.contrib import admin
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "actor",
        "action",
        "outcome",
        "document",
        "ip_address",
        "created_at",
    )

    list_filter = ("action", "outcome", "created_at")

    search_fields = (
        "actor__username",
        "action",
        "outcome",
        "document__title",
    )

    readonly_fields = (
        "actor",
        "document",
        "action",
        "outcome",
        "ip_address",
        "details",
        "created_at",
    )

    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
