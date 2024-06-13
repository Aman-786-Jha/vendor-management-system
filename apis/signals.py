# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F, Sum, Count, ExpressionWrapper, DurationField
from vendor_models.models import PurchaseOrder, Vendor

@receiver(post_save, sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, **kwargs):
    vendor = instance.vendor
    completed_orders = vendor.purchase_orders.filter(status='completed')
    total_orders = vendor.purchase_orders.count()
    acknowledged_orders = vendor.purchase_orders.exclude(acknowledgment_date__isnull=True)

    # On-Time Delivery Rate
    on_time_deliveries = completed_orders.filter(delivery_date__lte=F('delivery_date')).count()
    vendor.on_time_delivery_rate = (on_time_deliveries / completed_orders.count()) * 100 if completed_orders.exists() else 0

    # Quality Rating Average
    total_quality_ratings = completed_orders.aggregate(total=Sum('quality_rating'))['total'] or 0
    vendor.quality_rating_avg = total_quality_ratings / completed_orders.count() if completed_orders.exists() else 0

    # Average Response Time
    total_response_time_seconds = acknowledged_orders.annotate(
        response_time=ExpressionWrapper(
            F('acknowledgment_date') - F('issue_date'),
            output_field=DurationField()
        )
    ).aggregate(total=Sum('response_time'))['total'].total_seconds() if acknowledged_orders.exists() else 0
    average_response_time_seconds = total_response_time_seconds / acknowledged_orders.count() if acknowledged_orders.exists() else 0
    vendor.average_response_time = average_response_time_seconds / 3600  # Convert to hours

    # Fulfillment Rate
    fulfilled_orders = completed_orders.filter(status='completed').count()
    vendor.fulfillment_rate = (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0

    vendor.save()
