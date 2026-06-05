from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Notification, Order


@receiver(pre_save, sender=Order)
def _order_capture_previous_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return

    previous = Order.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    instance._previous_status = previous


@receiver(post_save, sender=Order)
def _order_status_notification(sender, instance, created, **kwargs):
    if created:
        return

    previous_status = getattr(instance, '_previous_status', None)
    if not previous_status or previous_status == instance.status:
        return

    def _create_notifications():
        message = f"Order {instance.order_number} status changed: {previous_status} → {instance.status}."

        customer_key = f"order:{instance.pk}:customer:status:{previous_status}->{instance.status}"
        Notification.objects.get_or_create(
            event_key=customer_key,
            defaults={
                'user': instance.customer,
                'order': instance,
                'message': message,
            },
        )

        if instance.seller_id:
            seller_key = f"order:{instance.pk}:seller:status:{previous_status}->{instance.status}"
            Notification.objects.get_or_create(
                event_key=seller_key,
                defaults={
                    'user': instance.seller,
                    'order': instance,
                    'message': message,
                },
            )

    transaction.on_commit(_create_notifications)
