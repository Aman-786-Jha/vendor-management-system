from django.db import models
from django.conf import settings
from .model_manager import VendorManagementUserManager 
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid 
import random 
import string 
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator



class CommonTimePicker(models.Model):
    """
    An abstract model in Django that provides two fields, `created_at` and `updated_at`, which automatically record the date and time when an object is created or updated.
    """
    created_at = models.DateTimeField("Created Date",auto_now_add=True)
    updated_at = models.DateTimeField("Updated Date",auto_now=True)

    class Meta:
        abstract = True


class VendorManagementUser(AbstractBaseUser, PermissionsMixin, CommonTimePicker):
    USER_TYPE_CHOICES = [
        ('Buyer', 'Buyer'),
        ('Vendor', 'Vendor'),
        ('Developer', 'Developer'),
        ('Admin', 'Admin'),
    ]
    user_type = models.CharField("User type", max_length=15,choices=USER_TYPE_CHOICES)
    name = models.CharField("Name", max_length=250,null= True, blank=True, db_index=True)
    email = models.EmailField("Email",max_length=100,null=False,blank=False,unique=True,db_index=True)
    password = models.CharField("password",max_length=100)
    address = models.TextField(max_length=250)
    contact_details = models.TextField(max_length=250)
    # vendor_buyer_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = VendorManagementUserManager()
    is_superuser = models.BooleanField("Superuser", default=False)
    is_active = models.BooleanField("Active",default=True)
    is_staff = models.BooleanField("Staff", default= False)


    def __str__(self):
        return f'{self.user_type}_{self.name}_{self.email}'
    


class Vendor(CommonTimePicker):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    vendor_code = models.CharField(max_length=50, unique=True, blank=True)
    on_time_delivery_date = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.user.name}_{self.user.email}'

    def generate_vendor_code(self):
        vendor_id = str(self.id) if self.id else '0'
        random_component = ''.join(random.choices(string.digits + string.ascii_letters, k=4))
        vendor_code = f"V_{vendor_id}_{random_component}"
        return vendor_code

    def save(self, *args, **kwargs):
        if not self.vendor_code:
            self.vendor_code = self.generate_vendor_code()
        super().save(*args, **kwargs)  # Save again to update the vendor_code





class Buyer(CommonTimePicker):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_profile')
    buyer_code = models.CharField(max_length=50, unique=True, blank=True)
    preferred_payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True
    )
    total_orders = models.PositiveIntegerField(default=0)
    last_order_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.name}_{self.user.email}'

    def increment_order_count(self):
        self.total_orders += 1
        self.last_order_date = timezone.now().date()
        self.save()

    def generate_buyer_code(self):
        buyer_id = str(self.id) if self.id else '0'
        random_component = ''.join(random.choices(string.digits + string.ascii_letters, k=4))
        buyer_code = f"B_{buyer_id}_{random_component}"
        return buyer_code

    def save(self, *args, **kwargs):
        if not self.buyer_code:
            super().save(*args, **kwargs)  # Save the instance to get an ID
            self.buyer_code = self.generate_buyer_code()
        super().save(*args, **kwargs)  # Save again to update the buyer_code



class Items(CommonTimePicker):
    item_name = models.CharField("Item Name",max_length=255, blank=True, null=True,db_index=True)
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE,related_name="items")
    available_quantity = models.PositiveBigIntegerField("Available Quantity")

    def __str__(self):
        return f"{self.item_name} selling by the vendor {self.vendor.user.name}"
    class Meta:  #showing new itmems  on top
        ordering = ['-id']




class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    buyer = models.ForeignKey(Buyer,on_delete=models.CASCADE,related_name='purchased_orders')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    # items = models.JSONField()
    items = models.ForeignKey(Items, on_delete=models.PROTECT, related_name='purchased_orders')   #I will use signal in this case
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1),])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('issued','Issued'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ],default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PO {self.po_number} - {self.vendor.user.name}"

    class Meta:
        ordering = ['-order_date']



class HistoricalPerformanceVendor(CommonTimePicker):
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT,related_name="historical_performance")
    date = models.DateTimeField(null=True,blank=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)


    def __str__(self):
        return f"vendor {self.vendor.user.name} fulfillment rate {self.fulfillment_rate}"