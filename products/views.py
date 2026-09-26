from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category, StockAdjustment
from .forms import ProductForm, CategoryForm, StockAdjustmentForm
from accounts.decorators import admin_required

@login_required
def product_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    low_stock_only = request.GET.get('low_stock', '')

    products = Product.objects.filter(is_active=True).select_related('category', 'supplier')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(brand__icontains=query) |
            Q(model_number__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if low_stock_only:
        products = [p for p in products if p.is_low_stock]

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'low_stock_only': low_stock_only,
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            # Log initial stock if stock > 0
            if product.current_stock > 0:
                StockAdjustment.objects.create(
                    product=product,
                    change_qty=product.current_stock,
                    previous_qty=0,
                    new_qty=product.current_stock,
                    reason='MANUAL',
                    notes='Initial Stock Entry',
                    created_by=request.user
                )
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect('products:product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add New Product'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    old_stock = product.current_stock
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            updated_product = form.save()
            new_stock = updated_product.current_stock
            if old_stock != new_stock:
                diff = new_stock - old_stock
                StockAdjustment.objects.create(
                    product=updated_product,
                    change_qty=diff,
                    previous_qty=old_stock,
                    new_qty=new_stock,
                    reason='MANUAL',
                    notes='Updated via product edit',
                    created_by=request.user
                )
            messages.success(request, f"Product '{updated_product.name}' updated successfully!")
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': f'Edit Product: {product.name}'})

@login_required
@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, f"Product '{product.name}' deleted/deactivated.")
        return redirect('products:product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def stock_adjust(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adj = form.save(commit=False)
            change = adj.change_qty
            if product.current_stock + change < 0:
                messages.error(request, f"Cannot adjust stock below 0! Current stock is {product.current_stock}.")
                return redirect('products:product_list')
            
            adj.product = product
            adj.previous_qty = product.current_stock
            adj.new_qty = product.current_stock + change
            adj.created_by = request.user
            adj.save()

            product.current_stock = adj.new_qty
            product.save()

            messages.success(request, f"Stock for '{product.name}' updated. New stock: {product.current_stock}")
            return redirect('products:product_list')
    else:
        form = StockAdjustmentForm()
    return render(request, 'products/stock_adjust_modal.html', {'form': form, 'product': product})

@login_required
def product_history(request, pk):
    product = get_object_or_404(Product, pk=pk)
    adjustments = product.stock_adjustments.all().select_related('created_by')
    return render(request, 'products/product_history.html', {'product': product, 'adjustments': adjustments})

@login_required
def category_list(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/category_list.html', {'categories': categories, 'form': form})

# AJAX endpoint to create a category quickly from the product form
@login_required
def category_create_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name is required.'})
        if Category.objects.filter(name__iexact=name).exists():
            cat = Category.objects.get(name__iexact=name)
            return JsonResponse({'success': True, 'id': cat.id, 'name': cat.name, 'exists': True})
        cat = Category.objects.create(name=name)
        return JsonResponse({'success': True, 'id': cat.id, 'name': cat.name, 'exists': False})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)


# JSON search endpoint for POS fast billing!
@login_required
def product_search_api(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.filter(is_active=True)
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(model_number__icontains=q) | Q(brand__icontains=q)
        )
    data = []
    for p in products[:20]:
        data.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'unit': p.unit,
            'sale_price': float(p.sale_price),
            'purchase_price': float(p.purchase_price),
            'current_stock': p.current_stock,
            'is_low_stock': p.is_low_stock,
        })
    return JsonResponse({'products': data})
