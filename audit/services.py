
from .models import AuditEvent


def record_event(
    *,
    actor,
    action,
    outcome="success",
    document=None,
    ip_address=None,
    details=None,
):
    return AuditEvent.objects.create(
        actor=actor if actor and actor.is_authenticated else None,
        document=document,
        action=action,
        outcome=outcome,
        ip_address=ip_address,
        details=details or {},
    )
