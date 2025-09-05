"""Order signals for notifications"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order
from .utils import notify_admins_new_order


@receiver(post_save, sender=Order)
def order_created_notify(sender, instance: Order, created: bool, **kwargs):
    """Send notification only when order first created (after commit so items are saved)."""
    if not created:
        return
    # Defer sending until after the surrounding atomic transaction commits
    try:
        transaction.on_commit(lambda o=instance: notify_admins_new_order(o))
    except Exception:
        # Fallback (should rarely happen)
        notify_admins_new_order(instance)
