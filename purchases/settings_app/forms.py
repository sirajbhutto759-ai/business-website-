from django import forms
from .models import ShopSettings

class ShopSettingsForm(forms.ModelForm):
    class Meta:
        model = ShopSettings
        fields = ['shop_name', 'subtitle', 'address', 'phone', 'whatsapp', 'email', 'ntn_number', 'invoice_footer', 'logo']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ntn_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_footer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
