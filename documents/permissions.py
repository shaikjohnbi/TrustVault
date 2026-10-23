
from .models import Document, DocumentGrant


def can_access_document(user, document, required_permission="read"):
    if not user.is_authenticated:
        return False

    # Document owner has full access.
    if document.owner_id == user.id:
        return True

    # Check explicitly granted permission.
    grant = DocumentGrant.objects.filter(
        document=document,
        user=user,
    ).first()

    if not grant:
        return False

    if required_permission == "read":
        return grant.permission in ("read", "edit")

    if required_permission == "edit":
        return grant.permission == "edit"

    return False
