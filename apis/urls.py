# urls.py
from django.urls import path
from .views import VendorCreateView, VendorListView, VendorDetailView, LoginView

urlpatterns = [
    path('vendors-create/', VendorCreateView.as_view(), name='vendor-create'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:vendor_id>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('login/', LoginView.as_view(), name='login'),
]
