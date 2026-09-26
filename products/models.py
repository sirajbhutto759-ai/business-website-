from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('Pcs', 'Pieces'),
        ('Meter', 'Meters'),
        ('Set', 'Sets'),
        ('Box', 'Boxes'),
        ('Kg', 'Kilograms'),
        ('Unit', 'Units'),
    ]

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU / Product Code")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True, verbose_name="Model")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='Pcs')
    
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    current_stock = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5, verbose_name="Minimum Stock Level")
    
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='supplied_products')
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock_level

    @property
    def stock_value_purchase(self):
        return self.current_stock * self.purchase_price

    @property
    def stock_value_sale(self):
        return self.current_stock * self.sale_price


class StockAdjustment(models.Model):
    REASON_CHOICES = [
        ('PURCHASE', 'Purchase Stock Addition'),
        ('SALE', 'Sale Stock Deduction'),
        ('SALE_CANCEL', 'Sale Cancellation Restock'),
        ('SERVICE', 'Service/Repair Usage'),
        ('MANUAL', 'Manual Stock Adjustment'),
        ('DAMAGE', 'Damaged / Lost Stock'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments')
    change_qty = models.IntegerField(help_text="Positive for addition, negative for reduction")
    previous_qty = models.IntegerField()
    new_qty = models.IntegerField()
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default='MANUAL')
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name}: {self.change_qty:+d} ({self.get_reason_display()})"
