from django.urls import path
from . import views

app_name = 'settings_app'

urlpatterns = [
    path('', views.shop_settings_view, name='shop_settings'),
    path('backup/', views.backup_restore_view, name='backup_restore'),
    path('backup/download/', views.download_backup, name='download_backup'),
    path('backup/restore/', views.restore_backup, name='restore_backup'),
    path('reset-database/', views.reset_database, name='reset_database'),
]
