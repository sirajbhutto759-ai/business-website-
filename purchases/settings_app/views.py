import io
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
from django.http import HttpResponse
from .models import ShopSettings
from .forms import ShopSettingsForm
from accounts.decorators import admin_required

@login_required
@admin_required
def shop_settings_view(request):
    settings_obj = ShopSettings.get_settings()
    if request.method == 'POST':
        form = ShopSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop Settings updated successfully!")
            return redirect('settings_app:shop_settings')
    else:
        form = ShopSettingsForm(instance=settings_obj)

    return render(request, 'settings_app/settings_form.html', {'form': form, 'shop_settings': settings_obj})


@login_required
@admin_required
def backup_restore_view(request):
    return render(request, 'settings_app/backup_restore.html')


@login_required
@admin_required
def download_backup(request):
    today = datetime.date.today().strftime('%Y%m%d_%H%M%S')
    filename = f"siraj_ups_solar_backup_{today}.json"

    out = io.StringIO()
    call_command('dumpdata', indent=2, stdout=out, exclude=['contenttypes', 'auth.permission'])
    data = out.getvalue()
    out.close()

    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@admin_required
def restore_backup(request):
    if request.method == 'POST' and request.FILES.get('backup_file'):
        backup_file = request.FILES['backup_file']
        try:
            content = backup_file.read().decode('utf-8')
            with open('temp_restore.json', 'w', encoding='utf-8') as f:
                f.write(content)

            call_command('loaddata', 'temp_restore.json')
            messages.success(request, "Database backup restored successfully!")
        except Exception as e:
            messages.error(request, f"Error restoring backup: {str(e)}")
        return redirect('settings_app:backup_restore')
    
@login_required
@admin_required
def reset_database(request):
    if request.method == 'POST':
        confirm = request.POST.get('confirm_text', '').strip()
        if confirm == 'RESET':
            from sales.models import Sale, SaleItem
            from purchases.models import Purchase, PurchaseItem
            from products.models import Product, StockAdjustment
            from customers.models import Customer, CustomerPayment
            from suppliers.models import Supplier
            from expenses.models import Expense
            from services.models import ServiceJob
            
            SaleItem.objects.all().delete()
            Sale.objects.all().delete()
            CustomerPayment.objects.all().delete()
            PurchaseItem.objects.all().delete()
            Purchase.objects.all().delete()
            StockAdjustment.objects.all().delete()
            Product.objects.all().delete()
            Customer.objects.all().delete()
            Supplier.objects.all().delete()
            Expense.objects.all().delete()
            ServiceJob.objects.all().delete()
            
            messages.success(request, "Database reset successfully! All operational records cleared cleanly.")
        else:
            messages.error(request, "Reset cancelled. You must type 'RESET' to confirm database deletion.")
    return redirect('settings_app:backup_restore')

