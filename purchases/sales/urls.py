from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('pos/', views.pos_billing, name='pos_billing'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('<int:pk>/print/thermal/', views.sale_print_thermal, name='sale_print_thermal'),
    path('<int:pk>/pdf/', views.sale_pdf, name='sale_pdf'),
    path('<int:pk>/cancel/', views.sale_cancel, name='sale_cancel'),
]
