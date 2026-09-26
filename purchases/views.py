import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import Purchase, PurchaseItem
from products.models import Product, StockAdjustment
from suppliers.models import Supplier

@login_required
def purchase_list(request):
    query = request.GET.get('q', '').strip()
    supplier_id = request.GET.get('supplier', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    purchases = Purchase.objects.select_related('supplier', 'created_by').all()

    if query:
        purchases = purchases.filter(purchase_no__icontains=query)

    if supplier_id:
        purchases = purchases.filter(supplier_id=supplier_id)

    if date_from:
        purchases = purchases.filter(purchase_date__gte=date_from)

    if date_to:
        purchases = purchases.filter(purchase_date__lte=date_to)

    suppliers = Supplier.objects.filter(is_active=True)

    return render(request, 'purchases/purchase_list.html', {
        'purchases': purchases,
        'suppliers': suppliers,
        'query': query,
        'selected_supplier': supplier_id,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def purchase_create(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                supplier_id = data.get('supplier_id')
                purchase_date = data.get('purchase_date') or datetime.date.today().strftime('%Y-%m-%d')
                payment_method = data.get('payment_method', 'CASH')
                paid_amount = float(data.get('paid_amount', 0))
                notes = data.get('notes', '').strip()
                items_data = data.get('items', [])

                if not items_data:
                    return JsonResponse({'success': False, 'error': 'Purchase must contain at least one product.'}, status=400)

                supplier = get_object_or_404(Supplier, id=supplier_id)
                purchase_no = Purchase.generate_purchase_no()

                purchase = Purchase.objects.create(
                    purchase_no=purchase_no,
                    supplier=supplier,
                    purchase_date=purchase_date,
                    payment_method=payment_method,
                    paid_amount=paid_amount,
                    notes=notes,
                    created_by=request.user
                )

                grand_total = 0.00
                for item in items_data:
                    product_id = item.get('product_id')
                    qty = int(item.get('qty', 1))
                    purchase_price = float(item.get('purchase_price', 0))

                    if qty <= 0:
                        raise ValueError("Quantity must be greater than zero.")

                    product = Product.objects.select_for_update().get(id=product_id)
                    item_total = purchase_price * qty
                    grand_total += item_total

                    PurchaseItem.objects.create(
                        purchase=purchase,
                        product=product,
                        purchase_price=purchase_price,
                        quantity=qty,
                        total_price=item_total
                    )

                    # Update stock and purchase price
                    prev_stock = product.current_stock
                    product.current_stock += qty
                    if purchase_price > 0:
                        product.purchase_price = purchase_price
                    product.save()

                    # Log stock adjustment
                    StockAdjustment.objects.create(
                        product=product,
                        change_qty=qty,
                        previous_qty=prev_stock,
                        new_qty=product.current_stock,
                        reason='PURCHASE',
                        notes=f"Purchase #{purchase.purchase_no}",
                        created_by=request.user
                    )

                purchase.grand_total = grand_total
                purchase.remaining_balance = max(0.00, grand_total - paid_amount)
                purchase.save()

                return JsonResponse({
                    'success': True,
                    'purchase_id': purchase.id,
                    'purchase_no': purchase.purchase_no,
                    'message': f"Purchase #{purchase.purchase_no} saved successfully!"
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    suppliers = Supplier.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    next_purchase_no = Purchase.generate_purchase_no()

    return render(request, 'purchases/purchase_form.html', {
        'suppliers': suppliers,
        'products': products,
        'next_purchase_no': next_purchase_no,
        'today': datetime.date.today().strftime('%Y-%m-%d')
    })


@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase.objects.select_related('supplier', 'created_by').prefetch_related('items__product'), pk=pk)
    return render(request, 'purchases/purchase_detail.html', {'purchase': purchase})
