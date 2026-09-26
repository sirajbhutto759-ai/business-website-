import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Supplier, SupplierPayment
from .forms import SupplierForm, SupplierPaymentForm
from accounts.decorators import admin_required

@login_required
def supplier_list(request):
    query = request.GET.get('q', '').strip()
    suppliers = Supplier.objects.filter(is_active=True)

    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) | Q(company__icontains=query) | Q(phone__icontains=query)
        )

    supplier_data = []
    for s in suppliers:
        supplier_data.append({
            'supplier': s,
            'total_purchases': s.get_total_purchases(),
            'total_paid': s.get_total_paid(),
            'payable': s.remaining_payable,
        })

    return render(request, 'suppliers/supplier_list.html', {
        'supplier_data': supplier_data,
        'query': query
    })

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            s = form.save()
            messages.success(request, f"Supplier '{s.name}' added successfully!")
            return redirect('suppliers:supplier_detail', pk=s.pk)
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Add New Supplier'})

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    purchases = supplier.purchases.filter(status='COMPLETED').order_by('-purchase_date')
    payments = supplier.supplier_payments.all().order_by('-payment_date')

    ledger = []
    for p in purchases:
        ledger.append({
            'type': 'PURCHASE',
            'date': p.purchase_date,
            'ref': p.purchase_no,
            'description': f"Purchase #{p.purchase_no}",
            'credit': p.grand_total,
            'debit': p.paid_amount,
            'obj': p,
        })
    for pm in payments:
        ledger.append({
            'type': 'PAYMENT',
            'date': pm.payment_date,
            'ref': pm.reference_no or f"PAY-{pm.id}",
            'description': f"Paid via {pm.get_payment_method_display()}",
            'credit': 0,
            'debit': pm.amount,
            'obj': pm,
        })
    ledger.sort(key=lambda x: str(x['date']), reverse=True)

    context = {
        'supplier': supplier,
        'total_purchases': supplier.get_total_purchases(),
        'total_paid': supplier.get_total_paid(),
        'payable': supplier.remaining_payable,
        'ledger': ledger,
        'payment_form': SupplierPaymentForm(initial={'payment_date': datetime.date.today()}),
    }
    return render(request, 'suppliers/supplier_detail.html', context)

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.name}' updated successfully!")
            return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': f'Edit Supplier: {supplier.name}'})

@login_required
@admin_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.is_active = False
        supplier.save()
        messages.success(request, f"Supplier '{supplier.name}' deactivated.")
        return redirect('suppliers:supplier_list')
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})

@login_required
def supplier_payment_add(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.supplier = supplier
            payment.created_by = request.user
            payment.save()
            messages.success(request, f"Paid Rs. {payment.amount} to {supplier.name}. Remaining Payable: Rs. {supplier.remaining_payable}")
            return redirect('suppliers:supplier_detail', pk=supplier.pk)
    return redirect('suppliers:supplier_detail', pk=supplier.pk)
