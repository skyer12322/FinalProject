from __future__ import annotations

from django.db.models import Count

from .models import Notification


def notifications_unread_count(request):
    """
    Adds unread notifications count to every template context.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"notifications_unread_count": 0}

    unread_count = (
        Notification.objects
        .filter(user=user, is_read=False)
        .aggregate(c=Count("id"))
        .get("c", 0)
    )
    return {"notifications_unread_count": unread_count or 0}

