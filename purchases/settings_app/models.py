from django.db import models

class ShopSettings(models.Model):
    shop_name = models.CharField(max_length=200, default="Siraj UPS and Solar")
    subtitle = models.CharField(max_length=255, default="UPS | Solar Systems | Batteries | Inverters | Accessories")
    address = models.TextField(default="Main Market, Shop #12, City Center")
    phone = models.CharField(max_length=50, default="+92 300 1234567")
    whatsapp = models.CharField(max_length=50, default="+92 300 1234567")
    email = models.EmailField(default="contact@sirajupssolar.com", blank=True)
    ntn_number = models.CharField(max_length=50, blank=True, help_text="NTN / Tax Number")
    invoice_footer = models.TextField(default="Thank you for choosing Siraj UPS and Solar! Goods once sold are non-refundable after 7 days.")
    logo = models.ImageField(upload_to='shop_logo/', blank=True, null=True)

    class Meta:
        verbose_name = "Shop Setting"
        verbose_name_plural = "Shop Settings"

    def __str__(self):
        return self.shop_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj
