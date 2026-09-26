from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]
