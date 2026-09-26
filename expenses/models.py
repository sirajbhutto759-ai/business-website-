from django.db import models
from django.contrib.auth.models import User
import datetime

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('EASYPAISA', 'Easypaisa'),
        ('JAZZCASH', 'JazzCash'),
        ('OTHER', 'Other'),
    ]

    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='expenses')
    expense_date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.category.name} - Rs. {self.amount} ({self.expense_date})"
