"""Order signals for notifications"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order
from .utils import notify_admins_new_order, notify_customer_order_status


@receiver(pre_save, sender=Order)
def cache_old_status(sender, instance: Order, **kwargs):
    if instance.pk:
        try:
            old = Order.objects.get(pk=instance.pk)
            instance._old_status = old.status  # type: ignore[attr-defined]
        except Order.DoesNotExist:  # pragma: no cover
            instance._old_status = None  # type: ignore[attr-defined]
    else:
        instance._old_status = None  # type: ignore[attr-defined]


@receiver(post_save, sender=Order)
def order_created_or_updated(sender, instance: Order, created: bool, **kwargs):
    def after_commit_notifications():
        # New order admin + customer initial state
        if created:
            notify_admins_new_order(instance)
            notify_customer_order_status(instance)
        else:
            old_status = getattr(instance, '_old_status', None)
            if old_status and old_status != instance.status:
                # Status changed
                notify_customer_order_status(instance)
    try:
        transaction.on_commit(after_commit_notifications)
    except Exception:
        after_commit_notifications()
