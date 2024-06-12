# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('api/vendors/', VendorListView.as_view(), name='vendor-list'),
    path('api/vendors/create/', VendorCreateView.as_view(), name='vendor-create'),
    path('api/vendors/login/', VendorLoginView.as_view(), name='vendor-login'),
    path('api/vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('api/vendors/signup/', VendorSignupView.as_view(), name='vendor_signup'),
]


