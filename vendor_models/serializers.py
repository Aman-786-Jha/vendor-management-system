# serializers.py

from rest_framework import serializers
from vendor_models.models import Vendor, VendorManagementUser

class VendorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Name is required.',
            'blank': 'Name cannot be blank',
        }
    )

    contact_details = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Contact details are required.',
            'blank': 'Contact details cannot be blank',
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

    class Meta:
        model = Vendor
        fields = ['id', 'user', 'vendor_code', 'name', 'contact_details', 'address', 'on_time_delivery_date', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']
        read_only_fields = ['vendor_code']

    def create(self, validated_data):
        user = VendorManagementUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            contact_details=validated_data['contact_details'],
            address=validated_data['address'],
            user_type='Vendor'
        )
        validated_data['user'] = user
        vendor = Vendor.objects.create(**validated_data)
        return vendor


