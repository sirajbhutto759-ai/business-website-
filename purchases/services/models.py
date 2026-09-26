from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
import datetime

class ServiceJob(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('UPS_REPAIR', 'UPS Repair'),
        ('BATTERY_REPLACEMENT', 'Battery Replacement'),
        ('SOLAR_INSTALLATION', 'Solar Installation'),
        ('INVERTER_INSTALLATION', 'Inverter Installation'),
        ('PANEL_INSTALLATION', 'Solar Panel Installation'),
        ('MAINTENANCE', 'Maintenance'),
        ('OTHER', 'Other Service'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELIVERED', 'Delivered'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('EASYPAISA', 'Easypaisa'),
        ('JAZZCASH', 'JazzCash'),
        ('OTHER', 'Other'),
    ]

    service_no = models.CharField(max_length=50, unique=True, verbose_name="Service ID")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default='UPS_REPAIR')
    description = models.TextField(help_text="Issue description / job specs")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    
    parts_materials_used = models.TextField(blank=True)
    labor_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    material_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    
    service_date = models.DateField(default=datetime.date.today)
    completion_date = models.DateField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-service_date', '-created_at']

    def __str__(self):
        return f"{self.service_no} - {self.get_service_type_display()} ({self.get_customer_name()})"

    def get_customer_name(self):
        if self.customer:
            return self.customer.name
        return self.customer_name or "Walk-in Customer"

    def get_customer_phone(self):
        if self.customer and self.customer.phone:
            return self.customer.phone
        return self.customer_phone or "N/A"

    @classmethod
    def generate_service_no(cls):
        today_str = datetime.date.today().strftime('%Y%m%d')
        prefix = f"SRV-{today_str}-"
        last_srv = cls.objects.filter(service_no__startswith=prefix).order_by('-id').first()
        if last_srv:
            try:
                seq = int(last_srv.service_no.split('-')[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"
