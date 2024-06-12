from django.urls import path
from .views import (
    VendorCreateView, VendorListView, VendorDetailView, VendorUpdateView, VendorDeleteView,
    BuyerCreateView, BuyerListView, BuyerDetailView, BuyerUpdateView, BuyerDeleteView,
    PurchaseOrderCreateView, PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderUpdateView, PurchaseOrderDeleteView,
    LoginView
)

urlpatterns = [
    path('vendors-create/', VendorCreateView.as_view(), name='vendor-create'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<int:vendor_id>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('vendors/<int:vendor_id>/update/', VendorUpdateView.as_view(), name='vendor-update'),
    path('vendors/<int:vendor_id>/delete/', VendorDeleteView.as_view(), name='vendor-delete'),
    path('buyers-create/', BuyerCreateView.as_view(), name='buyer-create'),
    path('buyers/', BuyerListView.as_view(), name='buyer-list'),
    path('buyers/<int:buyer_id>/', BuyerDetailView.as_view(), name='buyer-detail'),
    path('buyers/<int:buyer_id>/update/', BuyerUpdateView.as_view(), name='buyer-update'),
    path('buyers/<int:buyer_id>/delete/', BuyerDeleteView.as_view(), name='buyer-delete'),
    path('purchase-orders-create/', PurchaseOrderCreateView.as_view(), name='purchase-order-create'),
    path('purchase-orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('purchase-orders/<str:po_number>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
    path('purchase-orders/<str:po_number>/update/', PurchaseOrderUpdateView.as_view(), name='purchase-order-update'),
    path('purchase-orders/<str:po_number>/delete/', PurchaseOrderDeleteView.as_view(), name='purchase-order-delete'),
    path('login/', LoginView.as_view(), name='login'),
]
