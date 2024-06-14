from django.db.models.signals import post_save
from django.dispatch import receiver
from vendor_models.models import PurchaseOrder
from .performance_calculations import update_vendor_metrics

@receiver(post_save, sender=PurchaseOrder)
def handle_purchase_order_status_change(sender, instance, **kwargs):
    update_vendor_metrics(instance.vendor)
