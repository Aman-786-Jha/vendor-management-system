from django.db.models import F, Avg, Sum, Count, DurationField
from django.utils import timezone
from vendor_models.models import Vendor, PurchaseOrder, HistoricalPerformanceVendor

def calculate_on_time_delivery_rate(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    on_time_deliveries = completed_orders.filter(delivery_date__lte=F('delivery_date')).count()
    total_completed_orders = completed_orders.count()
    
    on_time_delivery_rate = (on_time_deliveries / total_completed_orders) * 100 if total_completed_orders > 0 else 0
    return on_time_delivery_rate

def calculate_quality_rating_avg(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    total_quality_ratings = completed_orders.aggregate(total=Sum('quality_rating'))['total'] or 0
    total_completed_orders = completed_orders.count()
    
    quality_rating_avg = total_quality_ratings / total_completed_orders if total_completed_orders > 0 else 0
    return quality_rating_avg

def calculate_average_response_time(vendor):
    acknowledged_orders = PurchaseOrder.objects.filter(vendor=vendor).exclude(acknowledgment_date__isnull=True)
    total_response_time_seconds = acknowledged_orders.aggregate(
        total=Sum(F('acknowledgment_date') - F('issue_date'), output_field=DurationField())
    )['total'].total_seconds() if acknowledged_orders.exists() else 0
    average_response_time_seconds = total_response_time_seconds / acknowledged_orders.count() if acknowledged_orders.exists() else 0
    average_response_time_hours = average_response_time_seconds / 3600  # Convert to hours
    return average_response_time_hours

def calculate_fulfillment_rate(vendor):
    total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
    fulfilled_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').count()
    
    fulfillment_rate = (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0
    return fulfillment_rate

def update_vendor_metrics(vendor):
    on_time_delivery_rate = calculate_on_time_delivery_rate(vendor)
    quality_rating_avg = calculate_quality_rating_avg(vendor)
    average_response_time = calculate_average_response_time(vendor)
    fulfillment_rate = calculate_fulfillment_rate(vendor)
    
    vendor.on_time_delivery_rate = on_time_delivery_rate
    vendor.quality_rating_avg = quality_rating_avg
    vendor.average_response_time = average_response_time
    vendor.fulfillment_rate = fulfillment_rate
    vendor.save()

    
    HistoricalPerformanceVendor.objects.create(
        vendor=vendor,
        date=timezone.now(),
        on_time_delivery_rate=on_time_delivery_rate,
        quality_rating_avg=quality_rating_avg,
        average_response_time=average_response_time,
        fulfillment_rate=fulfillment_rate
    )
