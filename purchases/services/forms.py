from django import forms
from .models import ServiceJob

class ServiceJobForm(forms.ModelForm):
    class Meta:
        model = ServiceJob
        fields = [
            'customer', 'customer_name', 'customer_phone',
            'service_type', 'description', 'status',
            'parts_materials_used', 'labor_charges', 'material_charges',
            'paid_amount', 'payment_method', 'service_date', 'completion_date'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Walk-in Name (if no customer profile)'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Issue description / Repair details'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'parts_materials_used': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. MOSFET 40N60, 12V Fan'}),
            'labor_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'material_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
