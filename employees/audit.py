from .models import AuditLog


def record_audit(request, action, module, object_name, description):
    """Store one readable HR activity entry after a successful change."""
    actor = request.user if request.user.is_authenticated else None
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        module=module,
        object_name=str(object_name)[:160],
        description=str(description)[:255],
    )
