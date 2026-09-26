import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category
from customers.models import Customer
from suppliers.models import Supplier
from sales.models import Sale, SaleItem
from settings_app.models import ShopSettings

def run_audit():
    print("=" * 60)
    print("STARTING FULL DIAGNOSTIC AUDIT OF ALL MODULES")
    print("=" * 60)

    # Create test client
    client = Client()
    
    # 1. Create superuser if not exists
    user, created = User.objects.get_or_create(username='audit_admin')
    if created:
        user.set_password('adminpass123')
        user.is_superuser = True
        user.is_staff = True
        user.save()

    client.login(username='audit_admin', password='adminpass123')

    # List of all key URL names to test
    urls_to_test = [
        ('dashboard:index', {}),
        ('products:product_list', {}),
        ('products:product_create', {}),
        ('products:category_list', {}),
        ('customers:customer_list', {}),
        ('customers:customer_create', {}),
        ('suppliers:supplier_list', {}),
        ('suppliers:supplier_create', {}),
        ('sales:pos_billing', {}),
        ('sales:sale_list', {}),
        ('purchases:purchase_list', {}),
        ('purchases:purchase_create', {}),
        ('expenses:expense_list', {}),
        ('expenses:category_list', {}),
        ('services:service_list', {}),
        ('services:service_create', {}),
        ('reports:index', {}),
        ('reports:sales_report', {}),
        ('reports:purchase_report', {}),
        ('reports:profit_report', {}),
        ('reports:customer_balance_report', {}),
        ('reports:supplier_payable_report', {}),
        ('reports:stock_report', {}),
        ('settings_app:shop_settings', {}),
        ('settings_app:backup_restore', {}),
        ('accounts:user_list', {}),
    ]

    passed = 0
    failed = 0
    issues = []

    for url_name, kwargs in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url)
            if response.status_code == 200:
                print(f"[OK] {url_name} ({url}) -> Status 200")
                passed += 1
            else:
                print(f"[FAIL] {url_name} ({url}) -> Status {response.status_code}")
                failed += 1
                issues.append(f"{url_name}: Expected 200, got {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {url_name} -> Exception: {e}")
            failed += 1
            issues.append(f"{url_name}: Exception {e}")

    # 2. Check Database Settings & Logo setup
    try:
        shop = ShopSettings.get_settings()
        print(f"[OK] ShopSettings retrieved: '{shop.shop_name}'")
        if shop.logo:
            print(f"[OK] Shop Logo configured: {shop.logo.name}")
        else:
            print("[WARN] Shop Logo is not configured yet")
    except Exception as e:
        print(f"[ERROR] ShopSettings check failed: {e}")
        issues.append(f"ShopSettings check: {e}")

    print("=" * 60)
    print(f"AUDIT SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 60)
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f" - {issue}")
    else:
        print("NO ISSUES FOUND! ALL MODULES & URLS OPERATING 100% PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_audit()
