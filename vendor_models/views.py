# views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from vendor_models.models import Vendor
from .serializers import VendorSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate




class VendorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            401: openapi.Response(description='Unauthorized', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            403: openapi.Response(description='Forbidden', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        },
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Token',
            ),
        ]
    )
    def get(self, request, pk):
        try:
            vendor = get_object_or_404(Vendor, id=pk)
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
            print("VendorDetailView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Vendor not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        request_body=VendorSerializer,
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        },
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Token',
            ),
        ]
    )
    def put(self, request, pk):
        try:
            vendor = get_object_or_404(Vendor, id=pk)
            serializer = VendorSerializer(vendor, data=request.data)
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
                    'responseMessage': 'Bad Request',
                    'responseData': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("VendorDetailView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='OK', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        },
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Token',
            ),
        ]
    )
    def delete(self, request, pk):
        try:
            vendor = get_object_or_404(Vendor, id=pk)
            vendor.delete()
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor deleted successfully.',
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print("VendorDetailView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer(many=True)),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        },
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer ',
                description='Token',
            ),
        ]
    )
    def get(self, request):
        try:
            vendors = Vendor.objects.all()
            serializer = VendorSerializer(vendors, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor list retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print("VendorListView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorCreateView(APIView):
    @swagger_auto_schema(
        request_body=VendorSerializer,
        responses={
            201: openapi.Response(description='Created', schema=VendorSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = VendorSerializer(data=request.data)
            if serializer.is_valid():
                vendor = serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Vendor created successfully.',
                        'responseData': VendorSerializer(vendor).data,
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(serializer.errors).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("VendorCreateView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





class VendorLoginView(APIView):

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description='OK', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Vendor code'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Vendor password'),
            },
            required=['username', 'password'],
        )
    )
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            vendor = authenticate(username=username, password=password)
            
            if vendor:
                refresh = RefreshToken.for_user(vendor)
                return Response({
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor authenticated successfully.',
                    'responseData': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            else:
                return Response({
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid credentials.',
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("VendorLoginView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class VendorSignupView(APIView):
    @swagger_auto_schema(
         request_body=VendorSerializer,
        responses={
            201: openapi.Response(description='Created', schema=VendorSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = VendorSerializer(data=request.data)
            if serializer.is_valid():
                vendor = serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Vendor created successfully.',
                        'responseData': VendorSerializer(vendor).data,
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(serializer.errors).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("VendorSignupView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
