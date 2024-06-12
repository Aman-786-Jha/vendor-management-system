# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from .serializers import LoginSerializer, VendorSerializer, VendorManagementUserSerializer
from vendor_models.models import *

class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(description='OK', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'Login successful.',
                        'responseData': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Bad Request',
                    'responseData': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorCreateView(APIView):
    @swagger_auto_schema(
        request_body=VendorManagementUserSerializer,
        responses={
            201: openapi.Response(description='Created', schema=VendorManagementUserSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = VendorManagementUserSerializer(data=request.data)
            print('serializer----->',serializer)
            if serializer.is_valid():
                user = serializer.save()
                vendor = Vendor.objects.create(user=user)
                vendor.save()
                vendor_serializer = VendorSerializer(vendor)
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Vendor created successfully.',
                        'responseData': vendor_serializer.data,
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer(many=True)),
        }
    )
    def get(self, request):
        try:
            vendors = Vendor.objects.all()
            serializer = VendorSerializer(vendors, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendors retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get(self, request, vendor_id):
        try:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            serializer = VendorSerializer(vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor details retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=VendorSerializer,
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def put(self, request, vendor_id):
        try:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            serializer = VendorSerializer(vendor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'Vendor updated successfully.',
                        'responseData': serializer.data,
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def delete(self, request, vendor_id):
        try:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            vendor.delete()
            return Response(
                {
                    'responseCode': status.HTTP_204_NO_CONTENT,
                    'responseMessage': 'Vendor deleted successfully.',
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

