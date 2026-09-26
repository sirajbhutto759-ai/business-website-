from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name

    def get_total_purchases(self):
        total = self.purchases.filter(status='COMPLETED').aggregate(models.Sum('grand_total'))['grand_total__sum']
        return total or Decimal('0.00')

    def get_total_paid(self):
        purchases_paid = self.purchases.filter(status='COMPLETED').aggregate(models.Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
        direct_paid = self.supplier_payments.aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        return purchases_paid + direct_paid

    @property
    def remaining_payable(self):
        return self.get_total_purchases() - self.get_total_paid()


class SupplierPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('EASYPAISA', 'Easypaisa'),
        ('JAZZCASH', 'JazzCash'),
        ('OTHER', 'Other'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    payment_date = models.DateField()
    reference_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Supplier Payment #{self.id} - {self.supplier.name} - Rs. {self.amount}"
