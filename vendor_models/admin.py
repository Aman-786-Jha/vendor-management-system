from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(VendorManagementUser)
admin.site.register(Buyer)
admin.site.register(Vendor)
admin.site.register(Items)
# admin.site.register(PurchaseOrder)
admin.site.register(HistoricalPerformanceVendor)


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'po_number', 'vendor', 'buyer', 'order_date', 'delivery_date', 'status', 'quantity', 'quality_rating')
    search_fields = ('po_number', 'vendor__user__name', 'buyer__user__name')
    list_filter = ('status', 'order_date', 'delivery_date')

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
