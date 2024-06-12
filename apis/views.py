from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from .serializers import *
from vendor_models.models import *
from vendor_models.models import *

# Manual parameter for Authorization header
authorization_param = openapi.Parameter(
    name='Authorization',
    in_=openapi.IN_HEADER,
    type=openapi.TYPE_STRING,
    required=True,
    default='Bearer ',
    description='Token',
)

class LoginView(APIView):
    permission_classes = [AllowAny]

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
            if serializer.is_valid():
                user = serializer.save()
                vendor = Vendor(user=user)
                vendor.vendor_code = vendor.generate_vendor_code()  # Ensure the vendor_code is generated
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
        manual_parameters=[authorization_param],
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
        manual_parameters=[authorization_param],
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
        manual_parameters=[authorization_param],
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
        manual_parameters=[authorization_param],
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

# Buyer Views
class BuyerCreateView(APIView):
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
            if serializer.is_valid():
                user = serializer.save()
                buyer = Buyer(user=user)
                buyer.buyer_code = buyer.generate_buyer_code()  # Ensure the buyer_code is generated
                buyer.save()
                buyer_serializer = VendorManagementUserSerializer(user)
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Buyer created successfully.',
                        'responseData': buyer_serializer.data,
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

# Buyer Views
class BuyerListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(description='OK', schema=BuyerSerializer(many=True)),
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get(self, request):
        try:
            buyers = Buyer.objects.all()
            serializer = BuyerSerializer(buyers, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyers retrieved successfully.',
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

        



# Buyer Views (continued)
class BuyerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(description='OK', schema=BuyerSerializer),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get(self, request, buyer_id):
        try:
            buyer = get_object_or_404(Buyer, id=buyer_id)
            serializer = BuyerSerializer(buyer)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyer details retrieved successfully.',
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

class BuyerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=VendorManagementUserSerializer,
        responses={
            200: openapi.Response(description='OK', schema=VendorManagementUserSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def put(self, request, buyer_id):
        try:
            buyer = get_object_or_404(Buyer, id=buyer_id)
            serializer = VendorManagementUserSerializer(buyer.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'Buyer updated successfully.',
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

class BuyerDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def delete(self, request, buyer_id):
        try:
            buyer = get_object_or_404(Buyer, id=buyer_id)
            buyer.user.delete()  # This will also delete the Buyer object due to cascading
            return Response(
                {
                    'responseCode': status.HTTP_204_NO_CONTENT,
                    'responseMessage': 'Buyer deleted successfully.',
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

# Purchase Order Views
class PurchaseOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=PurchaseOrderSerializer,
        responses={
            201: openapi.Response(description='Created', schema=PurchaseOrderSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = PurchaseOrderSerializer(data=request.data)
            if serializer.is_valid():
                purchase_order = serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Purchase Order created successfully.',
                        'responseData': serializer.data,
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

class PurchaseOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(description='OK', schema=PurchaseOrderSerializer(many=True)),
        }
    )
    def get(self, request):
        try:
            purchase_orders = PurchaseOrder.objects.all()
            serializer = PurchaseOrderSerializer(purchase_orders, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase Orders retrieved successfully.',
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

class PurchaseOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(description='OK', schema=PurchaseOrderSerializer),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get(self, request, po_number):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, po_number=po_number)
            serializer = PurchaseOrderSerializer(purchase_order)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase Order details retrieved successfully.',
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

class PurchaseOrderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=PurchaseOrderSerializer,
        responses={
            200: openapi.Response(description='OK', schema=PurchaseOrderSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def put(self, request, po_number):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, po_number=po_number)
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'Purchase Order updated successfully.',
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

class PurchaseOrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            204: openapi.Response(description='No Content'),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def delete(self, request, po_number):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, po_number=po_number)
            purchase_order.delete()
            return Response(
                {
                    'responseCode': status.HTTP_204_NO_CONTENT,
                    'responseMessage': 'Purchase Order deleted successfully.',
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

