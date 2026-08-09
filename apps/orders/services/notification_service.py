from ..models import Notification


def create_notification(user, title, message, notification_type=""):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )


def mark_as_read(notification_id, user):
    Notification.objects.filter(id=notification_id, user=user).update(is_read=True)


def mark_all_as_read(user):
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)


def get_unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()


def get_notifications(user, limit=50):
    return Notification.objects.filter(user=user)[:limit]
