import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from .models import Sale, SaleItem
from products.models import Product, StockAdjustment
from customers.models import Customer
from .pdf_utils import generate_invoice_pdf
from accounts.decorators import admin_required

@login_required
def pos_billing(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                customer_id = data.get('customer_id')
                walkin_name = data.get('walkin_name', '').strip()
                walkin_phone = data.get('walkin_phone', '').strip()
                payment_method = data.get('payment_method', 'CASH')
                overall_discount = float(data.get('overall_discount', 0))
                paid_amount = float(data.get('paid_amount', 0))
                notes = data.get('notes', '').strip()
                items_data = data.get('items', [])

                if not items_data:
                    return JsonResponse({'success': False, 'error': 'Invoice must contain at least one product.'}, status=400)

                customer = None
                if customer_id:
                    customer = Customer.objects.get(id=customer_id)

                invoice_no = Sale.generate_invoice_no()

                sale = Sale.objects.create(
                    invoice_no=invoice_no,
                    customer=customer,
                    customer_name_snapshot=walkin_name if not customer else customer.name,
                    customer_phone_snapshot=walkin_phone if not customer else customer.phone,
                    payment_method=payment_method,
                    overall_discount=overall_discount,
                    paid_amount=paid_amount,
                    notes=notes,
                    created_by=request.user,
                )

                subtotal = 0.00
                for item in items_data:
                    product_id = item.get('product_id')
                    qty = int(item.get('qty', 1))
                    unit_price = float(item.get('unit_price', 0))
                    discount = float(item.get('discount', 0))

                    if qty <= 0:
                        raise ValueError(f"Invalid quantity {qty} for product.")

                    product = Product.objects.select_for_update().get(id=product_id)

                    if product.current_stock < qty:
                        raise ValueError(f"Insufficient stock for '{product.name}'. Available: {product.current_stock}, Requested: {qty}")

                    item_total = (unit_price * qty) - discount
                    subtotal += item_total

                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        unit_price=unit_price,
                        purchase_price_snapshot=product.purchase_price,
                        quantity=qty,
                        item_discount=discount,
                        total_price=item_total
                    )

                    # Deduct stock and record adjustment
                    prev_stock = product.current_stock
                    product.current_stock -= qty
                    product.save()

                    StockAdjustment.objects.create(
                        product=product,
                        change_qty=-qty,
                        previous_qty=prev_stock,
                        new_qty=product.current_stock,
                        reason='SALE',
                        notes=f"Invoice #{sale.invoice_no}",
                        created_by=request.user
                    )

                grand_total = max(0.00, subtotal - overall_discount)
                remaining = grand_total - paid_amount

                sale.subtotal = subtotal
                sale.grand_total = grand_total
                sale.remaining_balance = max(0.00, remaining)

                if remaining <= 0:
                    sale.payment_status = 'PAID'
                elif paid_amount > 0:
                    sale.payment_status = 'PARTIAL'
                else:
                    sale.payment_status = 'UNPAID'

                sale.save()

                return JsonResponse({
                    'success': True,
                    'invoice_id': sale.id,
                    'invoice_no': sale.invoice_no,
                    'message': f"Invoice #{sale.invoice_no} created successfully!"
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    # GET Request: Render POS interface
    products = Product.objects.filter(is_active=True).select_related('category')
    customers = Customer.objects.filter(is_active=True)
    next_invoice_no = Sale.generate_invoice_no()

    return render(request, 'sales/pos_billing.html', {
        'products': products,
        'customers': customers,
        'next_invoice_no': next_invoice_no,
    })


@login_required
def sale_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    customer_id = request.GET.get('customer', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    sales = Sale.objects.select_related('customer', 'created_by').all()

    if query:
        sales = sales.filter(
            Q(invoice_no__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(customer_name_snapshot__icontains=query) |
            Q(customer_phone_snapshot__icontains=query)
        )

    if status:
        sales = sales.filter(status=status)

    if payment_status:
        sales = sales.filter(payment_status=payment_status)

    if customer_id:
        sales = sales.filter(customer_id=customer_id)

    if date_from:
        sales = sales.filter(sale_date__date__gte=date_from)

    if date_to:
        sales = sales.filter(sale_date__date__lte=date_to)

    customers = Customer.objects.filter(is_active=True)

    return render(request, 'sales/sale_list.html', {
        'sales': sales,
        'customers': customers,
        'query': query,
        'selected_status': status,
        'selected_payment_status': payment_status,
        'selected_customer': customer_id,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale.objects.select_related('customer', 'created_by').prefetch_related('items__product'), pk=pk)
    return render(request, 'sales/sale_detail.html', {'sale': sale})


@login_required
def sale_print_thermal(request, pk):
    sale = get_object_or_404(Sale.objects.select_related('customer').prefetch_related('items__product'), pk=pk)
    return render(request, 'sales/invoice_thermal.html', {'sale': sale})


@login_required
def sale_pdf(request, pk):
    sale = get_object_or_404(Sale.objects.select_related('customer').prefetch_related('items__product'), pk=pk)
    pdf_content = generate_invoice_pdf(sale)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice_{sale.invoice_no}.pdf"'
    return response


@login_required
@admin_required
def sale_cancel(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if sale.status == 'CANCELLED':
        messages.warning(request, f"Invoice #{sale.invoice_no} is already cancelled.")
        return redirect('sales:sale_detail', pk=sale.pk)

    if request.method == 'POST':
        with transaction.atomic():
            # Restore stock for each item
            for item in sale.items.all():
                product = item.product
                prev_stock = product.current_stock
                product.current_stock += item.quantity
                product.save()

                StockAdjustment.objects.create(
                    product=product,
                    change_qty=item.quantity,
                    previous_qty=prev_stock,
                    new_qty=product.current_stock,
                    reason='SALE_CANCEL',
                    notes=f"Restocked from Cancelled Invoice #{sale.invoice_no}",
                    created_by=request.user
                )

            sale.status = 'CANCELLED'
            sale.save()
            messages.success(request, f"Invoice #{sale.invoice_no} has been cancelled and stock has been restored.")
            return redirect('sales:sale_detail', pk=sale.pk)

    return render(request, 'sales/sale_confirm_cancel.html', {'sale': sale})
