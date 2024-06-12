from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(VendorManagementUser)
admin.site.register(Buyer)
admin.site.register(Vendor)
admin.site.register(Items)
admin.site.register(PurchaseOrder)
admin.site.register(HistoricalPerformanceVendor)
