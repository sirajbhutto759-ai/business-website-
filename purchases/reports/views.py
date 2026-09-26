import csv
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q
from django.http import HttpResponse
from sales.models import Sale, SaleItem
from purchases.models import Purchase
from expenses.models import Expense
from products.models import Product
from customers.models import Customer
from suppliers.models import Supplier
from accounts.decorators import admin_required

@login_required
def report_index(request):
    return render(request, 'reports/report_index.html')


@login_required
def sales_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    preset = request.GET.get('preset', 'this_month')
    export = request.GET.get('export', '')

    today = datetime.date.today()
    sales = Sale.objects.filter(status='COMPLETED')

    if preset == 'today':
        sales = sales.filter(sale_date__date=today)
    elif preset == 'this_week':
        start_week = today - datetime.timedelta(days=today.weekday())
        sales = sales.filter(sale_date__date__gte=start_week)
    elif preset == 'this_month':
        sales = sales.filter(sale_date__year=today.year, sale_date__month=today.month)
    elif preset == 'this_year':
        sales = sales.filter(sale_date__year=today.year)
    elif preset == 'custom':
        if date_from:
            sales = sales.filter(sale_date__date__gte=date_from)
        if date_to:
            sales = sales.filter(sale_date__date__lte=date_to)

    total_sales = sales.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
    total_paid = sales.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.00
    total_due = sales.aggregate(Sum('remaining_balance'))['remaining_balance__sum'] or 0.00

    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="Sales_Report_{today}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Invoice #', 'Date', 'Customer', 'Payment Method', 'Grand Total', 'Paid', 'Balance', 'Status'])
        for s in sales:
            writer.writerow([s.invoice_no, s.sale_date.strftime('%Y-%m-%d %H:%M'), s.get_customer_name(), s.get_payment_method_display(), s.grand_total, s.paid_amount, s.remaining_balance, s.get_payment_status_display()])
        return response

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_paid': total_paid,
        'total_due': total_due,
        'preset': preset,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'reports/sales_report.html', context)


@login_required
def purchase_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    preset = request.GET.get('preset', 'this_month')
    export = request.GET.get('export', '')

    today = datetime.date.today()
    purchases = Purchase.objects.filter(status='COMPLETED')

    if preset == 'today':
        purchases = purchases.filter(purchase_date=today)
    elif preset == 'this_month':
        purchases = purchases.filter(purchase_date__year=today.year, purchase_date__month=today.month)
    elif preset == 'custom':
        if date_from:
            purchases = purchases.filter(purchase_date__gte=date_from)
        if date_to:
            purchases = purchases.filter(purchase_date__lte=date_to)

    total_purchases = purchases.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
    total_paid = purchases.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0.00
    total_payable = purchases.aggregate(Sum('remaining_balance'))['remaining_balance__sum'] or 0.00

    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="Purchase_Report_{today}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Purchase #', 'Date', 'Supplier', 'Payment Method', 'Grand Total', 'Paid', 'Balance'])
        for p in purchases:
            writer.writerow([p.purchase_no, p.purchase_date, p.supplier.name if p.supplier else 'N/A', p.get_payment_method_display(), p.grand_total, p.paid_amount, p.remaining_balance])
        return response

    context = {
        'purchases': purchases,
        'total_purchases': total_purchases,
        'total_paid': total_paid,
        'total_payable': total_payable,
        'preset': preset,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'reports/purchase_report.html', context)


@login_required
@admin_required
def profit_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    preset = request.GET.get('preset', 'this_month')

    today = datetime.date.today()
    sales = Sale.objects.filter(status='COMPLETED')

    if preset == 'today':
        sales = sales.filter(sale_date__date=today)
    elif preset == 'this_month':
        sales = sales.filter(sale_date__year=today.year, sale_date__month=today.month)
    elif preset == 'this_year':
        sales = sales.filter(sale_date__year=today.year)
    elif preset == 'custom':
        if date_from:
            sales = sales.filter(sale_date__date__gte=date_from)
        if date_to:
            sales = sales.filter(sale_date__date__lte=date_to)

    total_revenue = 0.00
    total_cost = 0.00
    total_gross_profit = 0.00

    sale_profits = []
    for s in sales:
        profit = s.calculate_profit()
        total_revenue += float(s.grand_total)
        total_gross_profit += profit
        sale_profits.append({'sale': s, 'profit': profit})

    # Expenses in period
    expenses = Expense.objects.all()
    if preset == 'today':
        expenses = expenses.filter(expense_date=today)
    elif preset == 'this_month':
        expenses = expenses.filter(expense_date__year=today.year, expense_date__month=today.month)
    elif preset == 'this_year':
        expenses = expenses.filter(expense_date__year=today.year)
    elif preset == 'custom':
        if date_from:
            expenses = expenses.filter(expense_date__gte=date_from)
        if date_to:
            expenses = expenses.filter(expense_date__lte=date_to)

    total_expenses = float(expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00)
    net_profit = total_gross_profit - total_expenses

    context = {
        'sale_profits': sale_profits,
        'total_revenue': total_revenue,
        'total_gross_profit': total_gross_profit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'preset': preset,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'reports/profit_report.html', context)


@login_required
def customer_balance_report(request):
    customers = Customer.objects.filter(is_active=True)
    debtors = []
    total_due = 0.00

    for c in customers:
        bal = c.outstanding_balance
        if bal > 0:
            debtors.append({'customer': c, 'balance': bal, 'total_purchases': c.get_total_purchases(), 'total_paid': c.get_total_paid()})
            total_due += float(bal)

    debtors.sort(key=lambda x: x['balance'], reverse=True)

    return render(request, 'reports/customer_balance_report.html', {
        'debtors': debtors,
        'total_due': total_due,
    })


@login_required
def supplier_payable_report(request):
    suppliers = Supplier.objects.filter(is_active=True)
    payables = []
    total_payable = 0.00

    for s in suppliers:
        rem = s.remaining_payable
        if rem > 0:
            payables.append({'supplier': s, 'payable': rem, 'total_purchases': s.get_total_purchases(), 'total_paid': s.get_total_paid()})
            total_payable += float(rem)

    payables.sort(key=lambda x: x['payable'], reverse=True)

    return render(request, 'reports/supplier_payable_report.html', {
        'payables': payables,
        'total_payable': total_payable,
    })


@login_required
def stock_report(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    low_stock_only = request.GET.get('low_stock', '')

    if low_stock_only:
        products = [p for p in products if p.is_low_stock]

    total_purchase_val = sum(float(p.stock_value_purchase) for p in products)
    total_sale_val = sum(float(p.stock_value_sale) for p in products)

    return render(request, 'reports/stock_report.html', {
        'products': products,
        'total_purchase_val': total_purchase_val,
        'total_sale_val': total_sale_val,
        'low_stock_only': low_stock_only,
    })
