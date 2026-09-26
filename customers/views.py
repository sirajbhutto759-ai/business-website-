import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Customer, CustomerPayment
from .forms import CustomerForm, CustomerPaymentForm
from accounts.decorators import admin_required

@login_required
def customer_list(request):
    query = request.GET.get('q', '').strip()
    has_balance = request.GET.get('has_balance', '')

    customers = Customer.objects.filter(is_active=True)

    if query:
        customers = customers.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(address__icontains=query)
        )

    customer_data = []
    for c in customers:
        balance = c.outstanding_balance
        if has_balance == '1' and balance <= 0:
            continue
        customer_data.append({
            'customer': c,
            'total_purchases': c.get_total_purchases(),
            'total_paid': c.get_total_paid(),
            'balance': balance,
        })

    return render(request, 'customers/customer_list.html', {
        'customer_data': customer_data,
        'query': query,
        'has_balance': has_balance
    })

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c = form.save()
            messages.success(request, f"Customer '{c.name}' created successfully!")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': c.id, 'name': c.name, 'phone': c.phone})
            return redirect('customers:customer_detail', pk=c.pk)
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Add New Customer'})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sales.filter(status='COMPLETED').order_by('-sale_date')
    payments = customer.customer_payments.all().order_by('-payment_date')
    
    # Combined ledger entries ordered by date
    ledger = []
    for s in sales:
        ledger.append({
            'type': 'SALE',
            'date': s.sale_date,
            'ref': s.invoice_no,
            'description': f"Invoice #{s.invoice_no}",
            'debit': s.grand_total,
            'credit': s.paid_amount,
            'obj': s,
        })
    for p in payments:
        ledger.append({
            'type': 'PAYMENT',
            'date': p.payment_date,
            'ref': p.reference_no or f"PAY-{p.id}",
            'description': f"Udhaar Payment via {p.get_payment_method_display()}",
            'debit': 0,
            'credit': p.amount,
            'obj': p,
        })
    ledger.sort(key=lambda x: str(x['date']), reverse=True)

    context = {
        'customer': customer,
        'total_purchases': customer.get_total_purchases(),
        'total_paid': customer.get_total_paid(),
        'balance': customer.outstanding_balance,
        'ledger': ledger,
        'payment_form': CustomerPaymentForm(initial={'payment_date': datetime.date.today()}),
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.name}' updated successfully!")
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': f'Edit Customer: {customer.name}'})

@login_required
@admin_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.is_active = False
        customer.save()
        messages.success(request, f"Customer '{customer.name}' deactivated.")
        return redirect('customers:customer_list')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})

@login_required
def customer_payment_add(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.customer = customer
            payment.created_by = request.user
            payment.save()
            messages.success(request, f"Received Rs. {payment.amount} from {customer.name}. Updated Balance: Rs. {customer.outstanding_balance}")
            return redirect('customers:customer_detail', pk=customer.pk)
        else:
            messages.error(request, "Invalid payment details. Please check the form.")
    return redirect('customers:customer_detail', pk=customer.pk)

# JSON API search for customer autocomplete in Billing/POS
@login_required
def customer_search_api(request):
    q = request.GET.get('q', '').strip()
    customers = Customer.objects.filter(is_active=True)
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(phone__icontains=q))
    data = []
    for c in customers[:20]:
        data.append({
            'id': c.id,
            'name': c.name,
            'phone': c.phone,
            'balance': float(c.outstanding_balance)
        })
    return JsonResponse({'customers': data})
