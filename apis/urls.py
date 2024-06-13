from django.urls import path
from .views import (
    VendorCreateView, VendorListView, VendorDetailView, VendorUpdateView, VendorDeleteView,
    BuyerCreateView, BuyerListView, BuyerDetailView, BuyerUpdateView, BuyerDeleteView,
    PurchaseOrderCreateView, PurchaseOrderListView, PurchaseOrderDetailView, PurchaseOrderUpdateView, PurchaseOrderDeleteView,
    LoginView, VendorPerformanceView, AcknowledgePurchaseOrderView
)

urlpatterns = [
    #--------------------Vendors--------------------------------#
    path('vendors-create/', VendorCreateView.as_view(), name='vendor-create'),
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/<str:vendor_code>', VendorDetailView.as_view(), name='vendor-detail'),
    path('vendors/<str:vendor_code>/update/', VendorUpdateView.as_view(), name='vendor-update'),
    path('vendors/<str:vendor_code>/delete/', VendorDeleteView.as_view(), name='vendor-delete'),


    #----------------------Buyers-----------------------------------#
    path('buyers-create/', BuyerCreateView.as_view(), name='buyer-create'),
    path('buyers/', BuyerListView.as_view(), name='buyer-list'),
    path('buyers/<str:buyer_code>', BuyerDetailView.as_view(), name='buyer-detail'),
    path('buyers/<str:buyer_code>/update/', BuyerUpdateView.as_view(), name='buyer-update'),
    # path('buyers/<int:buyer_id>/delete/', BuyerDeleteView.as_view(), name='buyer-delete'),
    path('buyers/<str:buyer_code>/', BuyerDeleteView.as_view(), name='buyer-delete'),


    #------------------------Purchase Orders---------------------------#
    path('purchase-orders-create/', PurchaseOrderCreateView.as_view(), name='purchase-order-create'),
    path('purchase-orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('purchase-orders/<str:po_number>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
    path('purchase-orders/<str:po_number>/update/', PurchaseOrderUpdateView.as_view(), name='purchase-order-update'),
    path('purchase-orders/<str:po_number>/delete/', PurchaseOrderDeleteView.as_view(), name='purchase-order-delete'),


    path('vendors/<int:vendor_id>/performance/', VendorPerformanceView.as_view(), name='vendor_performance'),
    path('purchase_orders/<str:po_number>/acknowledge/', AcknowledgePurchaseOrderView.as_view(), name='purchase_order_acknowledge'),


    #-----------------------Login-----------------------------------------#
    path('login/', LoginView.as_view(), name='login'),
    
]
