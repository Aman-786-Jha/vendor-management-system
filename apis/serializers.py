# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from vendor_models.models import Vendor, VendorManagementUser
from django.contrib.auth import get_user_model
User = get_user_model()

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




from rest_framework import serializers
from vendor_models.models import VendorManagementUser

class VendorManagementUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
            'blank': 'Email cannot be blank',
        }
    )

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.',
        },
        write_only=True,
        min_length=8  # Minimum length validation
    )

    confirm_password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Confirm Password is required.',
        },
        write_only=True
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Name is required.',
            'blank': 'Name cannot be blank',
        }
    )
    address = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Address is required.',
            'blank': 'Address cannot be blank',
        }
    )
    contact_details = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Contact Details are required.',
            'blank': 'Contact Details cannot be blank',
        }
    )
        
    class Meta:
        model = User
        fields = ['user_type','name', 'email', 'contact_details','address' ,'password', 'confirm_password']
        extra_kwargs = {
            'user_type': {'required': True, 'error_messages': {'required': 'User type is required.'}},
            'name': {'required': True, 'error_messages': {'required': 'Name is required.'}},
            'email': {'required': True, 'error_messages': {'required': 'Email is required.'}},
            'password': {'write_only': True, 'required': True, 'error_messages': {'required': 'Password is required.'}},
            'address': {'required': True, 'error_messages': {'required': 'Address is required.'}},
            'contact_details': {'required': True, 'error_messages': {'required': 'Contact details are required.'}},
        }

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email has already been registered.")

        if password != confirm_password:
            raise serializers.ValidationError("Password does not matches.")

        return data


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


class VendorManagementUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorManagementUser
        fields = ['name', 'password', 'address', 'contact_details']
        extra_kwargs = {'password': {'write_only': True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set all fields to required
        for field in self.fields:
            self.fields[field].required = True

    def validate(self, data):
        # Add custom validation logic if needed
        if 'password' in data and len(data['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return data





from rest_framework import serializers
from vendor_models.models import Vendor

class VendorSerializer(serializers.ModelSerializer):
    user = VendorManagementUserUpdateSerializer()

    class Meta:
        model = Vendor
        fields = ['user', 'on_time_delivery_date', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        
        # Update fields on Vendor model instance
        instance.on_time_delivery_date = validated_data.get('on_time_delivery_date', instance.on_time_delivery_date)
        instance.quality_rating_avg = validated_data.get('quality_rating_avg', instance.quality_rating_avg)
        instance.average_response_time = validated_data.get('average_response_time', instance.average_response_time)
        instance.fulfillment_rate = validated_data.get('fulfillment_rate', instance.fulfillment_rate)
        
        # Handle nested serializer (VendorManagementUserUpdateSerializer)
        if user_data:
            user_instance = instance.user
            user_serializer = VendorManagementUserUpdateSerializer(user_instance, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise serializers.ValidationError(user_serializer.errors)
        
        # Save updated instance
        instance.save()
        return instance



from rest_framework import serializers
from vendor_models.models import PurchaseOrder, Vendor, Buyer, Items
from django.core.exceptions import ObjectDoesNotExist

class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_code = serializers.CharField(write_only=True, required=True)
    buyer = serializers.PrimaryKeyRelatedField(queryset=Buyer.objects.all(), required=False)
    items = serializers.PrimaryKeyRelatedField(queryset=Items.objects.all())
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all(), required=False)

    class Meta:
        model = PurchaseOrder
        fields = [
            'po_number', 'vendor', 'buyer', 'order_date', 'delivery_date', 
            'items', 'quantity', 'status', 'quality_rating', 
            'issue_date', 'acknowledgment_date', 'vendor_code'
        ]
        read_only_fields = ['po_number', 'order_date', 'issue_date']

    def validate(self, data):
        vendor_code = data.get('vendor_code')
        
        try:
            vendor = Vendor.objects.get(vendor_code=vendor_code)
        except Vendor.DoesNotExist:
            raise serializers.ValidationError({'vendor_code': 'Invalid vendor code.'})
        
        data['vendor'] = vendor
        
        try:
            # Attempt to retrieve the buyer associated with the logged-in user
            buyer = self.context['request'].user.buyer_profile
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Buyer profile does not exist for the logged-in user.')
        
        data['buyer'] = buyer
        
        return data

    def create(self, validated_data):
        validated_data.pop('vendor_code')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        return purchase_order

    def update(self, instance, validated_data):
        validated_data.pop('vendor_code', None)
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
    



class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'on_time_delivery_date',
            'quality_rating_avg',
            'average_response_time',
            'fulfillment_rate'
        ]



class AcknowledgePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number']
