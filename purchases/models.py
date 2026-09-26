from django.db import models
from django.contrib.auth.models import User
from suppliers.models import Supplier
from products.models import Product
import datetime

class Purchase(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('EASYPAISA', 'Easypaisa'),
        ('JAZZCASH', 'JazzCash'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    purchase_no = models.CharField(max_length=50, unique=True, verbose_name="Purchase #")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchases')
    purchase_date = models.DateField(default=datetime.date.today)
    
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "Unknown Supplier"
        return f"Purchase {self.purchase_no} - {supplier_name}"

    @classmethod
    def generate_purchase_no(cls):
        today_str = datetime.date.today().strftime('%Y%m%d')
        prefix = f"PUR-{today_str}-"
        last_pur = cls.objects.filter(purchase_no__startswith=prefix).order_by('-id').first()
        if last_pur:
            try:
                seq = int(last_pur.purchase_no.split('-')[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_items')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
