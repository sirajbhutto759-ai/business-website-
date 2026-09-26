from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from products.models import Product
import datetime

class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('EASYPAISA', 'Easypaisa'),
        ('JAZZCASH', 'JazzCash'),
        ('OTHER', 'Other'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
        ('UNPAID', 'Unpaid'),
    ]

    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    invoice_no = models.CharField(max_length=50, unique=True, verbose_name="Invoice #")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    customer_name_snapshot = models.CharField(max_length=200, blank=True)
    customer_phone_snapshot = models.CharField(max_length=50, blank=True)
    
    sale_date = models.DateTimeField(default=datetime.datetime.now)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    overall_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_no} - {self.get_customer_name()}"

    def get_customer_name(self):
        if self.customer:
            return self.customer.name
        return self.customer_name_snapshot or "Walk-in Customer"

    def get_customer_phone(self):
        if self.customer and self.customer.phone:
            return self.customer.phone
        return self.customer_phone_snapshot or "N/A"

    @property
    def change_due(self):
        if self.paid_amount > self.grand_total:
            return self.paid_amount - self.grand_total
        return 0.00

    def calculate_profit(self):
        # Profit = Total sale items revenue - Total sale items purchase cost - overall discount
        if self.status == 'CANCELLED':
            return 0.00
        items_profit = 0.00
        for item in self.items.all():
            items_profit += float((item.unit_price - item.purchase_price_snapshot) * item.quantity - item.item_discount)
        return max(0.00, items_profit - float(self.overall_discount))

    @classmethod
    def generate_invoice_no(cls):
        today_str = datetime.date.today().strftime('%Y%m%d')
        prefix = f"INV-{today_str}-"
        last_sale = cls.objects.filter(invoice_no__startswith=prefix).order_by('-id').first()
        if last_sale:
            try:
                seq = int(last_sale.invoice_no.split('-')[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    quantity = models.IntegerField(default=1)
    item_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
