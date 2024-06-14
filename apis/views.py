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
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
import re 
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
User = get_user_model()


# Pagination class for limiting the number of results per page
class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100

# Manual parameter for Authorization header
authorization_param = openapi.Parameter(
    name='Authorization',
    in_=openapi.IN_HEADER,
    type=openapi.TYPE_STRING,
    required=True,
    default='Bearer ',
    description='Token',
)

name_param_buyer = openapi.Parameter(
    'name',
    openapi.IN_QUERY,
    description="Name of the Buyer",
    type=openapi.TYPE_STRING
)

name_param_vendor = openapi.Parameter(
    'name',
    openapi.IN_QUERY,
    description="Name of the Vendor",
    type=openapi.TYPE_STRING
)

email_param = openapi.Parameter(
    'email',
    openapi.IN_QUERY,
    description="Email address",
    type=openapi.TYPE_STRING
)

contact_details_param = openapi.Parameter(
    'contact_details',
    openapi.IN_QUERY,
    description="Contact details",
    type=openapi.TYPE_STRING
)

address_param = openapi.Parameter(
    'address',
    openapi.IN_QUERY,
    description="Address",
    type=openapi.TYPE_STRING
)

page_param = openapi.Parameter(
    'page',
    openapi.IN_QUERY,
    description="Page number",
    type=openapi.TYPE_INTEGER
)

page_size_param = openapi.Parameter(
    'page_size',
    openapi.IN_QUERY,
    description="Number of items per page",
    type=openapi.TYPE_INTEGER
)


buyer_code_param = openapi.Parameter(
    'buyer_code',
    openapi.IN_PATH,
    description="Buyer code",
    type=openapi.TYPE_STRING,
    required=True
)


vendor_code_param = openapi.Parameter(
    'vendor_code',
    openapi.IN_PATH,
    description="Vendor code",
    type=openapi.TYPE_STRING,
    required=True
)


#############################  LOGIN   ###################################

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
            print(f'Login error--------> {e}')
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

################################  VENDOR VIEW  ############################################


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
            print('vendor create error-------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[
            authorization_param,
            name_param_vendor,
            email_param,
            contact_details_param,
            address_param,
            page_param,
            page_size_param
        ],
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            400: openapi.Response(
                description='Bad request.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(
                description='Unauthorized.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: openapi.Response(
                description='Vendor not found.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            # Retrieve query parameters
            name = request.GET.get('name')
            email = request.GET.get('email')
            contact_details = request.GET.get('contact_details')
            address = request.GET.get('address')

            # Filter vendors based on query parameters
            filters = {}
            if name:
                filters['user__name__icontains'] = name
            if email:
                filters['user__email__icontains'] = email
            if contact_details:
                filters['user__contact_details__icontains'] = contact_details
            if address:
                filters['user__address__icontains'] = address

            vendors = Vendor.objects.filter(**filters) if filters else Vendor.objects.all()

            # Apply pagination
            paginator = CustomPagination()
            page = paginator.paginate_queryset(vendors, request)

            # Check if there are any vendors
            if not page:
                return paginator.get_paginated_response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'No data found',
                        'responseData': [],
                    }
                )

            serializer = VendorSerializer(page, many=True)

            return paginator.get_paginated_response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendors retrieved successfully.',
                    'responseData': serializer.data,
                }
            )
        except Exception as e:
            print('vendor list error------>', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param, vendor_code_param],
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            404: openapi.Response(
                description='Not Found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def get(self, request, vendor_code):
        try:
            # Validate vendor_code format
            if not isinstance(vendor_code, str) or not re.match(r'^V_\d+_[a-zA-Z0-9]{4}$', vendor_code):
                raise ValidationError({
                    'vendor_code': 'Invalid vendor code format. '
                                 'It should start with "V_" '
                                 'and follow the pattern "V_<id>_<4 random characters>".'
                })

            # Check if vendor exists by vendor_code
            vendor = Vendor.objects.filter(vendor_code=vendor_code).first()
            if not vendor:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Vendor not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = VendorSerializer(vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor details retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as ve:
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid input',
                    'responseData': ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f'vendor detail error----------->{e}')
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class VendorUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         manual_parameters=[authorization_param, vendor_code_param],
#         request_body=VendorSerializer,
#         responses={
#             200: openapi.Response(
#                 description='OK',
#                 schema=VendorSerializer,
#             ),
#             400: openapi.Response(
#                 description='Bad Request',
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
#                         'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
#                     }
#                 )
#             ),
#             404: openapi.Response(
#                 description='Not Found',
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
#                         'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
#                         'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
#                     }
#                 )
#             ),
#             500: openapi.Response(
#                 description='Internal Server Error',
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
#                         'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
#                         'responseData': openapi.Schema(
#                             type=openapi.TYPE_OBJECT,
#                             properties={
#                                 'error': openapi.Schema(type=openapi.TYPE_STRING)
#                             }
#                         )
#                     }
#                 )
#             )
#         }
#     )
#     def put(self, request, vendor_code):
#         try:
#             vendor = Vendor.objects.get(vendor_code=vendor_code)
#             serializer = VendorSerializer(vendor, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(
#                     {
#                         'responseCode': status.HTTP_200_OK,
#                         'responseMessage': 'Vendor updated successfully.',
#                         'responseData': serializer.data,
#                     },
#                     status=status.HTTP_200_OK
#                 )
#             return Response(
#                 {
#                     'responseCode': status.HTTP_400_BAD_REQUEST,
#                     'responseMessage': serializer.errors,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Vendor.DoesNotExist:
#             return Response(
#                 {
#                     'responseCode': status.HTTP_404_NOT_FOUND,
#                     'responseMessage': 'Vendor not found.',
#                     'responseData': [],
#                 },
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             print(f'Error updating vendor: {e}')
#             return Response(
#                 {
#                     'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     'responseMessage': 'Internal Server Error',
#                     'responseData': {'error': str(e)},
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class  VendorUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param,vendor_code_param ],
        request_body=VendorManagementUserUpdateSerializer,
        responses={
            200: openapi.Response(description='OK', schema=VendorManagementUserUpdateSerializer),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(
                description='Not Found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def put(self, request, vendor_code):
        try:
            # Validate buyer_code format
            if not isinstance(vendor_code, str) or not re.match(r'^V_\d+_[a-zA-Z0-9]{4}$', vendor_code):
                raise ValidationError({
                    'buyer_code': 'Invalid buyer code format. '
                                 'It should start with "B_" '
                                 'and follow the pattern "B_<id>_<4 random characters>".'
                })

            # Check if buyer exists by buyer_code
            vendor = Vendor.objects.filter(vendor_code=vendor_code).first()
            if not vendor:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Vendor not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update the user associated with the buyer
            serializer = VendorManagementUserUpdateSerializer(vendor.user, data=request.data, partial=True)
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
        except ValidationError as ve:
            print('validation error------>', ve.detail)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid input',
                    'responseData': ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('vendor update error----->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VendorDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param, vendor_code_param],
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(
                description='Not Found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def delete(self, request, vendor_code):
        try:
            # Validate vendor_code format
            if not isinstance(vendor_code, str) or not re.match(r'^V_\d+_[a-zA-Z0-9]{4}$', vendor_code):
                raise ValidationError({
                    'vendor_code': 'Invalid vendor code format. '
                                 'It should start with "V_" '
                                 'and follow the pattern "V_<id>_<4 random characters>".'
                })

            # Check if vendor exists by vendor_code
            vendor = Vendor.objects.filter(vendor_code=vendor_code).first()
            if not vendor:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Vendor not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Delete the vendor
            # vendor.delete()
            vendor.user.delete()

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor deleted successfully.',
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as ve:
            print('validation error-------->', ve.detail)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid input',
                    'responseData': ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('vendor delete-------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

###############################  BUYER VIEW  #######################################################

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
            print("BuyerCreate Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Buyer Views
class BuyerListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[
            authorization_param,
            name_param_buyer,
            email_param,
            contact_details_param,
            address_param,
            page_param,
            page_size_param
        ],
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            400: openapi.Response(
                description='Bad request.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(
                description='Unauthorized.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: openapi.Response(
                description='Vendor not found.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            # Retrieve query parameters
            name = request.GET.get('name')
            email = request.GET.get('email')
            contact_details = request.GET.get('contact_details')
            address = request.GET.get('address')

            # Filter buyers based on query parameters
            filters = {}
            if name:
                filters['user__name__icontains'] = name
            if email:
                filters['user__email__icontains'] = email
            if contact_details:
                filters['user__contact_details__icontains'] = contact_details
            if address:
                filters['user__address__icontains'] = address

            buyers = Buyer.objects.filter(**filters) if filters else Buyer.objects.all()

            # Apply pagination
            paginator = CustomPagination()
            page = paginator.paginate_queryset(buyers, request)

            # Check if there are any buyers
            if not page:
                return paginator.get_paginated_response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'No data found',
                        'responseData': [],
                    }
                )

            serializer = BuyerSerializer(page, many=True)

            return paginator.get_paginated_response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyers retrieved successfully.',
                    'responseData': serializer.data,
                }
            )
        except Exception as e:
            print('buyer list error---------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        



# Buyer Views
class BuyerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param, buyer_code_param],
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            404: openapi.Response(
                description='Not Found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def get(self, request, buyer_code):
        try:
            # Validate buyer_code format
            if not isinstance(buyer_code, str) or not re.match(r'^B_\d+_[a-zA-Z0-9]{4}$', buyer_code):
                raise ValidationError({
                    'buyer_code': 'Invalid buyer code format. '
                                 'It should start with "B_" '
                                 'and follow the pattern "B_<id>_<4 random characters>".'
                })

            # Check if buyer exists by buyer_code
            buyer = Buyer.objects.filter(buyer_code=buyer_code).first()
            if not buyer:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Buyer not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = BuyerSerializer(buyer)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyer details retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as ve:
            print('validation error---------->', ve.detail)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid input',
                    'responseData': ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('buyer detail error----------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BuyerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param,buyer_code_param ],
        request_body=VendorManagementUserUpdateSerializer,
        responses={
            200: openapi.Response(description='OK', schema=VendorManagementUserUpdateSerializer),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: openapi.Response(
                description='Not Found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def put(self, request, buyer_code):
        try:
            # Validate buyer_code format
            if not isinstance(buyer_code, str) or not re.match(r'^B_\d+_[a-zA-Z0-9]{4}$', buyer_code):
                raise ValidationError({
                    'buyer_code': 'Invalid buyer code format. '
                                 'It should start with "B_" '
                                 'and follow the pattern "B_<id>_<4 random characters>".'
                })

            # Check if buyer exists by buyer_code
            buyer = Buyer.objects.filter(buyer_code=buyer_code).first()
            if not buyer:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Buyer not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update the user associated with the buyer
            serializer = VendorManagementUserUpdateSerializer(buyer.user, data=request.data, partial=True)
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
        except ValidationError as ve:
            print('validation error--------->', ve.detail)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid input',
                    'responseData': ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('buyer update error--------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BuyerDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                    }
                )
            ),
            404: openapi.Response(
                description='Not Found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                        'responseData': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'error': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            )
        }
    )
    def delete(self, request, buyer_code):
        try:
            # Validate buyer_code format
            if not re.match(r'^B_\d+_[a-zA-Z0-9]{4}$', buyer_code):
                raise ValidationError({'buyer_code': 'Invalid buyer code format. It should start with "B_" and follow the pattern "B_<id>_<4 random characters>".'})

            # Check if buyer exists by buyer_code
            buyer = Buyer.objects.filter(buyer_code=buyer_code).first()
            if not buyer:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Buyer not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # buyer.delete()
            
            # Delete the user associated with the buyer
            buyer.user.delete()  # This will also delete the Buyer object due to cascading

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyer deleted successfully.',
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as ve:
            print('validation error--------->', ve.detail)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Invalid input',
                    'responseData': ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f'buyer deleted error--------->{e}')
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

####################################   PURCHASE ORDER    ##############################################

# Purchase Order Views
class PurchaseOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=PurchaseOrderSerializer,
        responses={
            201: openapi.Response(description='Created', schema=PurchaseOrderSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        """
        You cannot call `.save()` after accessing `serializer.data`.If you need to access data before committing to the database then inspect 'serializer.validated_data' instead. 
        """
        try:
            serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
            print('user----->',request.user.name)
            if serializer.is_valid():
                # print('serializer data------>', serializer.data)
                print('serialize data------->',serializer.validated_data)
                purchase_order = serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Purchase Order created successfully.',
                        'responseData': serializer.data,
                    },
                    status=status.HTTP_201_CREATED
                )
            print('serializer data------>>>>>', serializer.data)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('purchase create error--------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class PurchaseOrderListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        manual_parameters=[authorization_param, name_param_vendor, page_param, page_size_param],
        responses={
            200: openapi.Response(description='OK', schema=PurchaseOrderSerializer(many=True)),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'responseCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                'responseMessage': openapi.Schema(type=openapi.TYPE_STRING),
                'responseData': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
            })),
        }
    )
    def get(self, request):
        try:
            user = request.user
            vendor_name = request.query_params.get('name', None)
            print('vendor_name-------->', vendor_name)

            # Check if the user is a buyer or a vendor and filter accordingly
            if hasattr(user, 'buyer_profile'):
                purchase_orders = PurchaseOrder.objects.filter(buyer=user.buyer_profile)
                if vendor_name:
                    purchase_orders = purchase_orders.filter(vendor__user__name__icontains=vendor_name)
            elif hasattr(user, 'vendor_profile'):
                purchase_orders = PurchaseOrder.objects.filter(vendor=user.vendor_profile)
                if vendor_name:
                    purchase_orders = purchase_orders.filter(vendor__user__name__icontains=vendor_name)
            else:
                return Response(
                    {
                        'responseCode': status.HTTP_400_BAD_REQUEST,
                        'responseMessage': 'User does not have a buyer or vendor profile.',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not purchase_orders.exists():
                if vendor_name:
                    return Response(
                        {
                            'responseCode': status.HTTP_200_OK,
                            'responseMessage': f'No purchase order from the vendor {vendor_name}.',
                            'responseData': [],
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'responseCode': status.HTTP_200_OK,
                            'responseMessage': 'No purchase order till now.',
                            'responseData': [],
                        },
                        status=status.HTTP_200_OK
                    )

            # Paginate the purchase orders
            paginator = CustomPagination()
            paginated_purchase_orders = paginator.paginate_queryset(purchase_orders, request)
            if not paginated_purchase_orders:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Page not found.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PurchaseOrderSerializer(paginated_purchase_orders, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print('purchase order list error---------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
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
            user = request.user

            # Ensure the user is a buyer
            if not hasattr(user, 'buyer_profile'):
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Purchase Order not found.',
                        'responseData': {},
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Filter purchase orders by po_number and the logged-in buyer
            purchase_order = PurchaseOrder.objects.filter(po_number=po_number, buyer=user.buyer_profile).first()
            if not purchase_order:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': f'No purchase order found with PO number {po_number}.',
                        'responseData': [],
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

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
            print('purchase order detail error---------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
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
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def put(self, request, po_number):
        try:
            # Ensure the user is a buyer
            if not hasattr(request.user, 'buyer_profile'):
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Purchase Order not found.',
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Retrieve the purchase order instance for the logged-in buyer
            purchase_order = get_object_or_404(PurchaseOrder, po_number=po_number, buyer=request.user.buyer_profile)
            
            # Update the purchase order instance with request data
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True, context={'request': request})
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
            else:
                return Response(
                    {
                        'responseCode': status.HTTP_400_BAD_REQUEST,
                        'responseMessage': serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Http404:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase Order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except ObjectDoesNotExist as e:
            print('object not found---------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print('purchase order update error------------>', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again later.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PurchaseOrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(description='OK'),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def delete(self, request, po_number):
        try:
            # Ensure the user is a buyer
            if not hasattr(request.user, 'buyer_profile'):
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Purchase Order not found.',
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Retrieve the purchase order instance for the logged-in user (buyer)
            purchase_order = get_object_or_404(PurchaseOrder, po_number=po_number, buyer=request.user.buyer_profile)
            
            # Delete the purchase order
            purchase_order.delete()

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase Order deleted successfully.',
                },
                status=status.HTTP_200_OK
            )

        except Http404:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase Order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            print('purchase order delete error------------->', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again later.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

#################################     Performance Metric       ####################################################

from .performance_calculations import *

class VendorPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        responses={
            200: openapi.Response(description='OK', schema=VendorPerformanceSerializer),
            404: openapi.Response(description='Not Found', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            500: openapi.Response(description='Internal Server Error', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get(self, request, vendor_id):
        try:
            vendor = get_object_or_404(Vendor, id=vendor_id)
            performance = vendor.historical_performance.latest('date')
            serializer = VendorPerformanceSerializer(performance)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor performance metrics retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except Vendor.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Vendor not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except HistoricalPerformanceVendor.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'No performance metrics found for this vendor.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print('performance metrics error------------>', e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

#################################  PURCHASE ORDER STATUS  ####################################

class AcknowledgePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
        ),
        responses={
            200: openapi.Response(description='OK'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error'),
        }
    )
    def post(self, request, po_id):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
            purchase_order.acknowledgment_date = timezone.now()
            purchase_order.status = 'acknowledged'
            purchase_order.save()
            update_vendor_metrics(purchase_order.vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order acknowledged successfully.',
                },
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class IssuePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
        ),
        responses={
            200: openapi.Response(description='OK'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error'),
        }
    )
    def post(self, request, po_id):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
            purchase_order.issue_date = timezone.now()
            purchase_order.status = 'issued'
            purchase_order.save()
            update_vendor_metrics(purchase_order.vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order issued successfully.',
                },
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompletePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
        ),
        responses={
            200: openapi.Response(description='OK'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error'),
        }
    )
    def post(self, request, po_id):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
            purchase_order.completion_date = timezone.now()
            purchase_order.status = 'completed'
            purchase_order.save()
            update_vendor_metrics(purchase_order.vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order completed successfully.',
                },
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CancelPurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[authorization_param],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
        ),
        responses={
            200: openapi.Response(description='OK'),
            404: openapi.Response(description='Not Found'),
            500: openapi.Response(description='Internal Server Error'),
        }
    )
    def post(self, request, po_id):
        try:
            purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
            purchase_order.status = 'cancelled'
            purchase_order.save()
            update_vendor_metrics(purchase_order.vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order cancelled successfully.',
                },
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



