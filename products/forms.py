from django import forms
from .models import Product, Category, StockAdjustment

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional details'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'brand', 'model_number',
            'unit', 'purchase_price', 'sale_price', 'current_stock',
            'min_stock_level', 'supplier', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 150Ah Tubular Battery'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BAT-150AH'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Phoenix, Osaka, Inverex'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TX-1800'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].empty_label = '-- No Category --'
        self.fields['supplier'].required = False
        self.fields['supplier'].empty_label = '-- No Supplier --'

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        instance_id = self.instance.id if self.instance else None
        if Product.objects.filter(sku__iexact=sku).exclude(id=instance_id).exists():
            raise forms.ValidationError("A product with this SKU / Code already exists.")
        return sku

    def clean(self):
        cleaned_data = super().clean()
        purchase_price = cleaned_data.get('purchase_price') or 0
        sale_price = cleaned_data.get('sale_price') or 0
        current_stock = cleaned_data.get('current_stock') or 0
        min_stock = cleaned_data.get('min_stock_level') or 0

        if purchase_price < 0:
            self.add_error('purchase_price', "Purchase price cannot be negative.")
        if sale_price < 0:
            self.add_error('sale_price', "Sale price cannot be negative.")
        if current_stock < 0:
            self.add_error('current_stock', "Stock cannot be negative.")
        if min_stock < 0:
            self.add_error('min_stock_level', "Minimum stock cannot be negative.")

        return cleaned_data


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['change_qty', 'reason', 'notes']
        widgets = {
            'change_qty': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '+5 or -2'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason details'}),
        }
