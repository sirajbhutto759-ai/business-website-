from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/', views.product_create, name='product_create'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('<int:pk>/adjust-stock/', views.stock_adjust, name='stock_adjust'),
    path('<int:pk>/history/', views.product_history, name='product_history'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add-ajax/', views.category_create_ajax, name='category_create_ajax'),
    path('api/search/', views.product_search_api, name='product_search_api'),
]
