# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from vendor_models.models import Vendor, VendorManagementUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.', code='authorization')
        else:
            raise serializers.ValidationError('Must include "email" and "password".', code='authorization')

        attrs['user'] = user
        return attrs

# class VendorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Vendor
#         fields = ['user', 'vendor_code', 'on_time_delivery_date', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

# class VendorManagementUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VendorManagementUser
#         fields = ['user_type', 'name', 'email', 'password', 'address', 'contact_details']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = VendorManagementUser.objects.create_user(
#             user_type=validated_data['user_type'],
#             name=validated_data['name'],
#             email=validated_data['email'],
#             password=validated_data['password'],
#             address=validated_data['address'],
#             contact_details=validated_data['contact_details']
#         )
#         return user



from rest_framework import serializers
from vendor_models.models import VendorManagementUser

class VendorManagementUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorManagementUser
        fields = ['user_type', 'name', 'email', 'password', 'address', 'contact_details']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = VendorManagementUser.objects.create_user(
            user_type=validated_data['user_type'],
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password'],
            address=validated_data['address'],
            contact_details=validated_data['contact_details']
        )
        return user

    def update(self, instance, validated_data):
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.contact_details = validated_data.get('contact_details', instance.contact_details)
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()
        return instance


from rest_framework import serializers
from vendor_models.models import Buyer

class BuyerSerializer(serializers.ModelSerializer):
    user = VendorManagementUserSerializer()

    class Meta:
        model = Buyer
        fields = ['user', 'buyer_code', 'preferred_payment_method', 'total_orders', 'last_order_date', 'notes']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = VendorManagementUser.objects.create_user(**user_data)
        buyer = Buyer.objects.create(user=user, **validated_data)
        return buyer

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = VendorManagementUserSerializer(instance=instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()

        instance.preferred_payment_method = validated_data.get('preferred_payment_method', instance.preferred_payment_method)
        instance.total_orders = validated_data.get('total_orders', instance.total_orders)
        instance.last_order_date = validated_data.get('last_order_date', instance.last_order_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()

        return instance






from rest_framework import serializers
from vendor_models.models import Vendor

class VendorSerializer(serializers.ModelSerializer):
    user = VendorManagementUserSerializer()

    class Meta:
        model = Vendor
        fields = ['user', 'vendor_code', 'on_time_delivery_date', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = VendorManagementUserSerializer.create(VendorManagementUserSerializer(), validated_data=user_data)
        vendor, created = Vendor.objects.update_or_create(user=user, **validated_data)
        return vendor

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        instance.on_time_delivery_date = validated_data.get('on_time_delivery_date', instance.on_time_delivery_date)
        instance.quality_rating_avg = validated_data.get('quality_rating_avg', instance.quality_rating_avg)
        instance.average_response_time = validated_data.get('average_response_time', instance.average_response_time)
        instance.fulfillment_rate = validated_data.get('fulfillment_rate', instance.fulfillment_rate)

        user_serializer = VendorManagementUserSerializer(instance=user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

        instance.save()
        return instance



from rest_framework import serializers
from vendor_models.models import PurchaseOrder, Buyer, Vendor, Items

class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all())
    buyer = serializers.PrimaryKeyRelatedField(queryset=Buyer.objects.all())
    items = serializers.PrimaryKeyRelatedField(queryset=Items.objects.all())

    class Meta:
        model = PurchaseOrder
        fields = [
            'po_number', 'vendor', 'buyer', 'order_date', 'delivery_date', 
            'items', 'quantity', 'status', 'quality_rating', 
            'issue_date', 'acknowledgment_date'
        ]
        read_only_fields = ['po_number', 'order_date', 'issue_date']

    def create(self, validated_data):
        # Handle the creation of a new purchase order
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        return purchase_order

    def update(self, instance, validated_data):
        # Update the fields of the purchase order
        instance.vendor = validated_data.get('vendor', instance.vendor)
        instance.buyer = validated_data.get('buyer', instance.buyer)
        instance.delivery_date = validated_data.get('delivery_date', instance.delivery_date)
        instance.items = validated_data.get('items', instance.items)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.status = validated_data.get('status', instance.status)
        instance.quality_rating = validated_data.get('quality_rating', instance.quality_rating)
        instance.acknowledgment_date = validated_data.get('acknowledgment_date', instance.acknowledgment_date)
        
        instance.save()
        return instance
