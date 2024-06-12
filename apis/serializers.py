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

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['user', 'vendor_code', 'on_time_delivery_date', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

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
