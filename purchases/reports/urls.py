from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index, name='index'),
    path('sales/', views.sales_report, name='sales_report'),
    path('purchases/', views.purchase_report, name='purchase_report'),
    path('profit/', views.profit_report, name='profit_report'),
    path('customer-balances/', views.customer_balance_report, name='customer_balance_report'),
    path('supplier-payables/', views.supplier_payable_report, name='supplier_payable_report'),
    path('stock/', views.stock_report, name='stock_report'),
]
