from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import UserProfile
from products.models import Product, Category, StockAdjustment
from customers.models import Customer, CustomerPayment
from suppliers.models import Supplier
from sales.models import Sale, SaleItem
from purchases.models import Purchase, PurchaseItem
from settings_app.models import ShopSettings
import json

class SirajUpsSolarWorkflowTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create Admin & Cashier User
        self.admin = User.objects.create_superuser('testadmin', 'admin@test.com', 'adminpass123')
        self.cashier = User.objects.create_user('testcashier', 'cashier@test.com', 'cashierpass123')
        self.cashier.profile.role = UserProfile.ROLE_STAFF
        self.cashier.profile.save()

        # Shop Settings
        ShopSettings.get_settings()

        # Category & Products
        self.cat = Category.objects.create(name='Battery')
        self.sup = Supplier.objects.create(name='Osaka Supplier', company='Osaka')
        self.product = Product.objects.create(
            name='150Ah Battery',
            sku='BAT-150-TEST',
            category=self.cat,
            purchase_price=40000,
            sale_price=45000,
            current_stock=10,
            min_stock_level=2,
            supplier=self.sup
        )

        # Customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone='0300-1112233'
        )

    def test_user_login(self):
        response = self.client.post('/accounts/login/', {'username': 'testadmin', 'password': 'adminpass123'})
        self.assertEqual(response.status_code, 302)

    def test_pos_invoice_creation_and_stock_reduction(self):
        self.client.force_login(self.cashier)
        
        initial_stock = self.product.current_stock # 10
        payload = {
            'customer_id': self.customer.id,
            'payment_method': 'CASH',
            'overall_discount': 1000,
            'paid_amount': 40000,
            'items': [
                {'product_id': self.product.id, 'qty': 2, 'unit_price': 45000, 'discount': 0}
            ]
        }

        # POST POS Invoice
        response = self.client.post(
            '/sales/pos/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.content)
        self.assertTrue(res_data['success'])

        # Verify stock decreased by 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, initial_stock - 2)

        # Verify Sale object totals
        sale = Sale.objects.get(id=res_data['invoice_id'])
        self.assertEqual(sale.subtotal, 90000)
        self.assertEqual(sale.grand_total, 89000)
        self.assertEqual(sale.paid_amount, 40000)
        self.assertEqual(sale.remaining_balance, 49000)
        self.assertEqual(sale.payment_status, 'PARTIAL')

        # Verify Customer Udhaar Balance equals 49000
        self.assertEqual(self.customer.outstanding_balance, 49000)

    def test_purchase_stock_increase(self):
        self.client.force_login(self.admin)
        initial_stock = self.product.current_stock # 10

        payload = {
            'supplier_id': self.sup.id,
            'payment_method': 'CASH',
            'paid_amount': 200000,
            'items': [
                {'product_id': self.product.id, 'qty': 5, 'purchase_price': 40000}
            ]
        }

        response = self.client.post(
            '/purchases/add/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify stock increased by 5
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, initial_stock + 5)

    def test_customer_udhaar_payment(self):
        self.client.force_login(self.cashier)

        # Create a sale with balance
        sale = Sale.objects.create(
            invoice_no='INV-TEST-001',
            customer=self.customer,
            subtotal=100000,
            grand_total=100000,
            paid_amount=60000,
            remaining_balance=40000,
            status='COMPLETED'
        )
        # Customer balance should be 40000
        self.assertEqual(self.customer.outstanding_balance, 40000)

        # Pay 20000 towards Udhaar
        response = self.client.post(f'/customers/{self.customer.id}/payment/', {
            'amount': '20000',
            'payment_method': 'CASH',
            'payment_date': '2026-09-26',
            'reference_no': 'REC-123'
        })
        self.assertEqual(response.status_code, 302)

        # Remaining customer balance should be 20000
        self.assertEqual(self.customer.outstanding_balance, 20000)

    def test_sale_cancellation_restocks_inventory(self):
        self.client.force_login(self.admin)

        # Create sale
        sale = Sale.objects.create(
            invoice_no='INV-TEST-RESTOCK',
            customer=self.customer,
            subtotal=45000,
            grand_total=45000,
            paid_amount=45000,
            remaining_balance=0,
            status='COMPLETED'
        )
        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            unit_price=45000,
            quantity=2,
            total_price=90000
        )
        self.product.current_stock -= 2
        self.product.save()

        stock_before_cancel = self.product.current_stock # 8

        # Cancel sale
        response = self.client.post(f'/sales/{sale.id}/cancel/')
        self.assertEqual(response.status_code, 302)

        sale.refresh_from_db()
        self.assertEqual(sale.status, 'CANCELLED')

        # Check stock restored by 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, stock_before_cancel + 2)
