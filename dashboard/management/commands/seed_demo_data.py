import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from settings_app.models import ShopSettings
from products.models import Category, Product, StockAdjustment
from customers.models import Customer, CustomerPayment
from suppliers.models import Supplier, SupplierPayment
from sales.models import Sale, SaleItem
from purchases.models import Purchase, PurchaseItem
from expenses.models import ExpenseCategory, Expense
from services.models import ServiceJob

class Command(BaseCommand):
    help = 'Seeds initial sample data for Siraj UPS and Solar'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding Siraj UPS and Solar demo data..."))

        # 1. Shop Settings
        shop = ShopSettings.get_settings()
        shop.shop_name = "Siraj UPS and Solar"
        shop.subtitle = "UPS | Solar Systems | Batteries | Inverters | Accessories"
        shop.address = "Main Market, Shop #12, Commercial Zone, Lahore"
        shop.phone = "+92 300 1234567"
        shop.whatsapp = "+92 300 1234567"
        shop.email = "info@sirajupssolar.com"
        shop.invoice_footer = "Thank you for choosing Siraj UPS and Solar! Goods once sold are non-refundable after 7 days."
        shop.save()

        # 2. Users & Roles
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@sirajupssolar.com', 'first_name': 'Siraj', 'last_name': 'Owner', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.profile.role = UserProfile.ROLE_ADMIN
        admin_user.profile.phone = "+92 300 1234567"
        admin_user.profile.save()

        cashier_user, _ = User.objects.get_or_create(
            username='cashier',
            defaults={'email': 'cashier@sirajupssolar.com', 'first_name': 'Ali', 'last_name': 'Khan', 'is_staff': True}
        )
        cashier_user.set_password('cashier123')
        cashier_user.save()
        cashier_user.profile.role = UserProfile.ROLE_STAFF
        cashier_user.profile.phone = "+92 302 9876543"
        cashier_user.profile.save()

        # 3. Categories
        cat_names = [
            'UPS', 'Solar Panel', 'Solar Inverter', 'Battery',
            'Charge Controller', 'Solar Cable', 'AC Cable', 'DC Cable',
            'Breaker', 'Fuse', 'Connector', 'Installation Material', 'Other'
        ]
        cat_objs = {}
        for cname in cat_names:
            cat_objs[cname], _ = Category.objects.get_or_create(name=cname)

        # 4. Suppliers
        s1, _ = Supplier.objects.get_or_create(name="Osaka / Phoenix Battery Co", company="Osaka Batteries", phone="0300-1112233", address="Industrial Zone, Karachi")
        s2, _ = Supplier.objects.get_or_create(name="Longi & Canadian Solar Imports", company="Solar Global Imports", phone="0321-4445566", address="Main Boulevard, Lahore")
        s3, _ = Supplier.objects.get_or_create(name="Inverex & Crown Micro Tech", company="Inverex Solar", phone="0312-7778899", address="Rawalpindi Market")

        # 5. Products
        sample_products = [
            {'name': '150Ah Tubular Battery', 'sku': 'BAT-150AH', 'cat': 'Battery', 'brand': 'Osaka', 'purchase': 42000, 'sale': 48000, 'stock': 12, 'min': 4, 'supplier': s1},
            {'name': '200Ah Tubular Battery', 'sku': 'BAT-200AH', 'cat': 'Battery', 'brand': 'Phoenix', 'purchase': 53000, 'sale': 60000, 'stock': 8, 'min': 3, 'supplier': s1},
            {'name': '550W Mono PERC Solar Panel', 'sku': 'PNL-550W', 'cat': 'Solar Panel', 'brand': 'Longi', 'purchase': 24000, 'sale': 28000, 'stock': 25, 'min': 10, 'supplier': s2},
            {'name': '585W N-Type Solar Panel', 'sku': 'PNL-585W', 'cat': 'Solar Panel', 'brand': 'Jinko', 'purchase': 27000, 'sale': 31500, 'stock': 18, 'min': 5, 'supplier': s2},
            {'name': '1KW Solar Inverter Hybrid', 'sku': 'INV-1KW', 'cat': 'Solar Inverter', 'brand': 'Crown', 'purchase': 38000, 'sale': 44000, 'stock': 6, 'min': 2, 'supplier': s3},
            {'name': '3KW Solar Inverter Hybrid', 'sku': 'INV-3KW', 'cat': 'Solar Inverter', 'brand': 'Inverex Nitro', 'purchase': 85000, 'sale': 98000, 'stock': 4, 'min': 2, 'supplier': s3},
            {'name': '5KW Solar Inverter Hybrid', 'sku': 'INV-5KW', 'cat': 'Solar Inverter', 'brand': 'Inverex Veyron', 'purchase': 145000, 'sale': 165000, 'stock': 3, 'min': 2, 'supplier': s3},
            {'name': 'UPS 1000VA Digital', 'sku': 'UPS-1000', 'cat': 'UPS', 'brand': 'Homage', 'purchase': 22000, 'sale': 26000, 'stock': 5, 'min': 2, 'supplier': s3},
            {'name': 'Solar Cable 6mm Copper', 'sku': 'CBL-6MM', 'cat': 'Solar Cable', 'brand': 'Pakistan Cables', 'purchase': 180, 'sale': 240, 'unit': 'Meter', 'stock': 200, 'min': 50, 'supplier': s2},
            {'name': 'MC4 Connector Pair', 'sku': 'MC4-PAIR', 'cat': 'Connector', 'brand': 'Generic', 'purchase': 120, 'sale': 180, 'stock': 50, 'min': 15, 'supplier': s2},
        ]

        prod_objs = {}
        for pdata in sample_products:
            p, created = Product.objects.get_or_create(
                sku=pdata['sku'],
                defaults={
                    'name': pdata['name'],
                    'category': cat_objs[pdata['cat']],
                    'brand': pdata['brand'],
                    'purchase_price': pdata['purchase'],
                    'sale_price': pdata['sale'],
                    'unit': pdata.get('unit', 'Pcs'),
                    'current_stock': pdata['stock'],
                    'min_stock_level': pdata['min'],
                    'supplier': pdata['supplier'],
                    'description': f"Premium quality {pdata['name']}"
                }
            )
            prod_objs[pdata['sku']] = p

        # 6. Customers
        c1, _ = Customer.objects.get_or_create(name="Muhammad Tariq", phone="0300-9876543", address="House #45, Gulberg III, Lahore", notes="Regular customer")
        c2, _ = Customer.objects.get_or_create(name="Zahid Mahmood", phone="0321-5551234", address="Shop #5, Model Town Market", notes="Solar installation client")
        c3, _ = Customer.objects.get_or_create(name="Usman Ali", phone="0333-4447788", address="Johar Town Phase 2")

        # 7. Expense Categories & Sample Expenses
        exp_cat_rent, _ = ExpenseCategory.objects.get_or_create(name="Shop Rent")
        exp_cat_elec, _ = ExpenseCategory.objects.get_or_create(name="Electricity")
        exp_cat_sal, _ = ExpenseCategory.objects.get_or_create(name="Salary")
        exp_cat_trans, _ = ExpenseCategory.objects.get_or_create(name="Transport")

        today = datetime.date.today()
        Expense.objects.get_or_create(category=exp_cat_rent, expense_date=today, defaults={'amount': 35000, 'description': 'Monthly Shop Rent', 'created_by': admin_user})
        Expense.objects.get_or_create(category=exp_cat_elec, expense_date=today, defaults={'amount': 12500, 'description': 'Electricity Bill Sept', 'created_by': admin_user})
        Expense.objects.get_or_create(category=exp_cat_trans, expense_date=today, defaults={'amount': 2500, 'description': 'Cartage for panels', 'created_by': admin_user})

        # 8. Sample Sales / Invoices
        if not Sale.objects.exists():
            inv_no = Sale.generate_invoice_no()
            sale1 = Sale.objects.create(
                invoice_no=inv_no,
                customer=c1,
                customer_name_snapshot=c1.name,
                customer_phone_snapshot=c1.phone,
                sale_date=datetime.datetime.now(),
                subtotal=96000,
                overall_discount=1000,
                grand_total=95000,
                paid_amount=60000,
                remaining_balance=35000,
                payment_method='CASH',
                payment_status='PARTIAL',
                created_by=cashier_user
            )

            p_bat = prod_objs['BAT-150AH']
            SaleItem.objects.create(
                sale=sale1,
                product=p_bat,
                unit_price=48000,
                purchase_price_snapshot=p_bat.purchase_price,
                quantity=2,
                item_discount=0,
                total_price=96000
            )

        # 9. Sample Service Job
        if not ServiceJob.objects.exists():
            ServiceJob.objects.create(
                service_no=ServiceJob.generate_service_no(),
                customer=c3,
                customer_name=c3.name,
                customer_phone=c3.phone,
                service_type='UPS_REPAIR',
                description='UPS 1000VA not charging battery. Replaced MOSFETs & fan.',
                status='COMPLETED',
                parts_materials_used='2x IRF1404 MOSFETs, 12V Cooling Fan',
                labor_charges=1500,
                material_charges=1200,
                total_charges=2700,
                paid_amount=2700,
                remaining_balance=0,
                payment_method='CASH',
                service_date=today,
                created_by=admin_user
            )

        self.stdout.write(self.style.SUCCESS("Sample demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("Admin login: admin / admin123"))
        self.stdout.write(self.style.SUCCESS("Cashier login: cashier / cashier123"))
