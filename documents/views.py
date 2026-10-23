

import json
import os
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

from audit.services import record_event
from .models import Document, DocumentGrant
from .permissions import can_access_document


User = get_user_model()

ALLOWED_EXTENSIONS = {
    ".pdf", ".txt", ".png", ".jpg", ".jpeg", ".docx"
}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


def client_ip(request):
    return request.META.get("REMOTE_ADDR")


def log_event(
    request,
    action,
    document=None,
    outcome="success",
    details=None,
):
    record_event(
        actor=request.user,
        document=document,
        action=action,
        outcome=outcome,
        ip_address=client_ip(request),
        details=details or {},
    )


@login_required
@require_GET
def document_list(request):
    from django.db.models import Q

    documents = Document.objects.filter(
        Q(owner=request.user) | Q(grants__user=request.user)
    ).select_related("owner").distinct()

    search = request.GET.get("search", "").strip()
    if search:
        documents = documents.filter(
            Q(title__icontains=search)
            | Q(owner__username__icontains=search)
        )

    owner = request.GET.get("owner", "").strip()
    if owner:
        documents = documents.filter(
            owner__username__icontains=owner
        )

    category = request.GET.get("category", "").strip()
    if category:
        documents = documents.filter(category__icontains=category)

    date_filter = request.GET.get("date", "").strip()
    if date_filter:
        from datetime import date

        try:
            date.fromisoformat(date_filter)
        except ValueError:
            return JsonResponse(
                {"error": "Date must use YYYY-MM-DD format."},
                status=400,
            )

        documents = documents.filter(created_at__date=date_filter)

    data = [
        {
            "id": document.id,
            "title": document.title,
            "category": document.category,
            "created_at": document.created_at.isoformat(),
            "owner": document.owner.username,
        }
        for document in documents.order_by("-created_at")
    ]

    return JsonResponse({"documents": data})


@login_required
@require_http_methods(["GET", "PATCH", "DELETE"])
def document_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == "GET":
        if not can_access_document(request.user, document, "read"):
            log_event(
                request,
                "document_view",
                document,
                "denied",
                {"reason": "permission_denied"},
            )
            return JsonResponse(
                {"error": "Access denied."},
                status=403,
            )

        log_event(request, "document_view", document)

        return JsonResponse({
            "id": document.id,
            "title": document.title,
            "category": document.category,
            "description": document.description,
            "owner": document.owner.username,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        })

    if not can_access_document(request.user, document, "edit"):
        log_event(
            request,
            "document_modify",
            document,
            "denied",
            {"method": request.method},
        )
        return JsonResponse(
            {"error": "Access denied."},
            status=403,
        )

    if request.method == "PATCH":
        try:
            payload = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Invalid JSON."},
                status=400,
            )

        allowed_fields = {"title", "category", "description"}

        if not isinstance(payload, dict) or not payload:
            return JsonResponse(
                {"error": "Provide document fields to update."},
                status=400,
            )

        if set(payload) - allowed_fields:
            return JsonResponse(
                {"error": "Unsupported fields."},
                status=400,
            )

        for field, value in payload.items():
            if not isinstance(value, str):
                return JsonResponse(
                    {"error": f"Invalid value for {field}."},
                    status=400,
                )

        if "title" in payload and not payload["title"].strip():
            return JsonResponse(
                {"error": "Title cannot be empty."},
                status=400,
            )

        for field, value in payload.items():
            setattr(
                document,
                field,
                value.strip() if field in {"title", "category"} else value,
            )

        document.save()

        log_event(
            request,
            "document_update",
            document,
            details={"fields": list(payload.keys())},
        )

        return JsonResponse({
            "message": "Document updated successfully.",
            "id": document.id,
            "title": document.title,
        })

    log_event(
        request,
        "document_delete",
        document,
        details={"title": document.title},
    )

    stored_file = document.file
    stored_name = stored_file.name if stored_file else None

    document.delete()

    if stored_name and stored_file.storage.exists(stored_name):
        stored_file.storage.delete(stored_name)

    return JsonResponse({
        "message": "Document deleted successfully."
    })


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def document_grants(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if document.owner_id != request.user.id:
        log_event(
            request,
            "permission_manage",
            document,
            "denied",
            {"reason": "owner_only"},
        )
        return JsonResponse(
            {"error": "Only the owner can manage permissions."},
            status=403,
        )

    if request.method == "GET":
        grants = document.grants.select_related("user").all()

        return JsonResponse({
            "grants": [
                {
                    "id": grant.id,
                    "username": grant.user.username,
                    "permission": grant.permission,
                    "created_at": grant.created_at.isoformat(),
                }
                for grant in grants
            ]
        })

    if request.method == "POST":
        try:
            payload = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Invalid JSON."},
                status=400,
            )

        if not isinstance(payload, dict):
            return JsonResponse(
                {"error": "JSON object required."},
                status=400,
            )

        username = payload.get("username")
        permission = payload.get("permission", "read")

        if not isinstance(username, str) or not username.strip():
            return JsonResponse(
                {"error": "A username is required."},
                status=400,
            )

        if permission not in {"read", "edit"}:
            return JsonResponse(
                {"error": "Permission must be read or edit."},
                status=400,
            )

        target_user = User.objects.filter(
            username=username.strip()
        ).first()

        if target_user is None:
            return JsonResponse(
                {"error": "User not found."},
                status=404,
            )

        if target_user.pk == request.user.pk:
            return JsonResponse(
                {"error": "You already own this document."},
                status=400,
            )

        grant, created = DocumentGrant.objects.update_or_create(
            document=document,
            user=target_user,
            defaults={"permission": permission},
        )

        log_event(
            request,
            "permission_grant" if created else "permission_change",
            document,
            details={
                "target_username": target_user.username,
                "permission": permission,
            },
        )

        return JsonResponse(
            {
                "message": (
                    "Permission granted."
                    if created
                    else "Permission updated."
                ),
                "grant_id": grant.id,
                "username": grant.user.username,
                "permission": grant.permission,
            },
            status=201 if created else 200,
        )

    grant_id = request.GET.get("grant_id", "").strip()

    if not grant_id.isdigit():
        return JsonResponse(
            {"error": "Provide a valid grant_id."},
            status=400,
        )

    grant = document.grants.filter(
        pk=int(grant_id)
    ).select_related("user").first()

    if grant is None:
        return JsonResponse(
            {"error": "Grant not found."},
            status=404,
        )

    target_username = grant.user.username
    target_permission = grant.permission
    grant.delete()

    log_event(
        request,
        "permission_revoke",
        document,
        details={
            "target_username": target_username,
            "permission": target_permission,
        },
    )

    return JsonResponse({"message": "Permission revoked."})


@login_required
@require_POST
def document_upload(request):
    uploaded_file = request.FILES.get("file")
    title = request.POST.get("title", "").strip()
    category = request.POST.get("category", "").strip()
    description = request.POST.get("description", "")

    if uploaded_file is None:
        return JsonResponse(
            {"error": "Choose a file to upload."},
            status=400,
        )

    if not title:
        return JsonResponse(
            {"error": "Document title is required."},
            status=400,
        )

    if uploaded_file.size == 0:
        return JsonResponse(
            {"error": "Empty files are not allowed."},
            status=400,
        )

    if uploaded_file.size > MAX_UPLOAD_SIZE:
        return JsonResponse(
            {"error": "Maximum file size is 10 MB."},
            status=400,
        )

    safe_filename = os.path.basename(uploaded_file.name)
    extension = Path(safe_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return JsonResponse(
            {"error": "File type not allowed."},
            status=400,
        )

    # Validate image content. Correct indentation is important here.
    if extension in {".png", ".jpg", ".jpeg"}:
        try:
            uploaded_file.seek(0)

            with Image.open(uploaded_file) as image:
                expected_format = {
                    ".png": "PNG",
                    ".jpg": "JPEG",
                    ".jpeg": "JPEG",
                }[extension]

                if image.format != expected_format:
                    return JsonResponse(
                        {"error": "File content does not match its extension."},
                        status=400,
                    )

                image.verify()

            uploaded_file.seek(0)

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError,
        ):
            return JsonResponse(
                {"error": "Invalid or corrupted image file."},
                status=400,
            )

    elif extension == ".pdf":
        uploaded_file.seek(0)
        if uploaded_file.read(5) != b"%PDF-":
            return JsonResponse(
                {"error": "Invalid PDF file."},
                status=400,
            )
        uploaded_file.seek(0)

    elif extension == ".txt":
        uploaded_file.seek(0)
        content = uploaded_file.read()

        if b"\x00" in content:
            return JsonResponse(
                {"error": "Invalid text file."},
                status=400,
            )

        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            return JsonResponse(
                {"error": "Text file must use UTF-8 encoding."},
                status=400,
            )

        uploaded_file.seek(0)

    elif extension == ".docx":
        import zipfile

        uploaded_file.seek(0)

        try:
            with zipfile.ZipFile(uploaded_file) as archive:
                if "word/document.xml" not in archive.namelist():
                    return JsonResponse(
                        {"error": "Invalid DOCX document."},
                        status=400,
                    )

                if archive.testzip() is not None:
                    return JsonResponse(
                        {"error": "Corrupted DOCX file."},
                        status=400,
                    )
        except (OSError, ValueError, zipfile.BadZipFile):
            return JsonResponse(
                {"error": "Invalid or corrupted DOCX file."},
                status=400,
            )
        finally:
            uploaded_file.seek(0)

    document = Document(
        owner=request.user,
        title=title,
        category=category,
        description=description,
    )

    try:
        document.file.save(
            safe_filename,
            uploaded_file,
            save=False,
        )
        document.save()
    except Exception:
        if document.file and document.file.name:
            try:
                document.file.storage.delete(document.file.name)
            except OSError:
                pass

        return JsonResponse(
            {"error": "Unable to store the uploaded file."},
            status=500,
        )

    log_event(
        request,
        "document_upload",
        document,
        details={"filename": safe_filename},
    )

    return JsonResponse(
        {
            "message": "Document uploaded successfully.",
            "id": document.id,
            "title": document.title,
        },
        status=201,
    )


@login_required
@require_GET
def document_download(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if not can_access_document(request.user, document, "read"):
        log_event(
            request,
            "document_download",
            document,
            "denied",
            {"reason": "permission_denied"},
        )
        return JsonResponse(
            {"error": "File not found."},
            status=404,
        )

    if not document.file:
        log_event(
            request,
            "document_download",
            document,
            "failed",
            {"reason": "file_missing"},
        )
        return JsonResponse(
            {"error": "File not found."},
            status=404,
        )

    try:
        file_handle = document.file.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        log_event(
            request,
            "document_download",
            document,
            "failed",
            {"reason": "stored_file_unavailable"},
        )
        return JsonResponse(
            {"error": "Stored file is unavailable."},
            status=404,
        )

    log_event(request, "document_download", document)

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=os.path.basename(document.file.name),
    )
