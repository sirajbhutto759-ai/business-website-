import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from sales.models import Sale
from purchases.models import Purchase
from expenses.models import Expense
from products.models import Product
from customers.models import Customer
from suppliers.models import Supplier

@login_required
def index(request):
    today = datetime.date.today()

    # Today Stats
    today_sales_qs = Sale.objects.filter(sale_date__date=today, status='COMPLETED')
    today_sales = float(today_sales_qs.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00)

    today_purchases_qs = Purchase.objects.filter(purchase_date=today, status='COMPLETED')
    today_purchases = float(today_purchases_qs.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00)

    today_expenses_qs = Expense.objects.filter(expense_date=today)
    today_expenses = float(today_expenses_qs.aggregate(Sum('amount'))['amount__sum'] or 0.00)

    today_gross_profit = sum(s.calculate_profit() for s in today_sales_qs)
    today_profit = today_gross_profit - today_expenses

    # Total Receivables (Customer Balances)
    all_customers = Customer.objects.filter(is_active=True)
    total_receivables = sum(float(c.outstanding_balance) for c in all_customers if c.outstanding_balance > 0)

    # Total Payables (Supplier Balances)
    all_suppliers = Supplier.objects.filter(is_active=True)
    total_payables = sum(float(s.remaining_payable) for s in all_suppliers if s.remaining_payable > 0)

    # Counts
    all_products = Product.objects.filter(is_active=True)
    total_products = all_products.count()
    low_stock_count = sum(1 for p in all_products if p.is_low_stock)
    total_customers = all_customers.count()

    # Recent Invoices
    recent_sales = Sale.objects.select_related('customer').order_by('-sale_date')[:5]

    # Low stock list for quick alert
    low_stock_products = [p for p in all_products if p.is_low_stock][:5]

    context = {
        'today_sales': today_sales,
        'today_purchases': today_purchases,
        'today_profit': today_profit,
        'today_expenses': today_expenses,
        'total_receivables': total_receivables,
        'total_payables': total_payables,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def chart_data_api(request):
    today = datetime.date.today()
    
    # 1. Daily Sales (last 7 days)
    days_labels = []
    daily_sales_data = []
    daily_purchases_data = []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        days_labels.append(d.strftime('%a %d %b'))
        
        s_sum = Sale.objects.filter(sale_date__date=d, status='COMPLETED').aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
        p_sum = Purchase.objects.filter(purchase_date=d, status='COMPLETED').aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00
        
        daily_sales_data.append(float(s_sum))
        daily_purchases_data.append(float(p_sum))

    # 2. Monthly Sales & Profit (last 6 months)
    months_labels = []
    monthly_sales_data = []
    monthly_profit_data = []

    for i in range(5, -1, -1):
        # Calculate year and month
        month_dt = today.replace(day=1) - datetime.timedelta(days=i*30)
        m_year = month_dt.year
        m_month = month_dt.month
        months_labels.append(month_dt.strftime('%b %Y'))

        sales_m = Sale.objects.filter(sale_date__year=m_year, sale_date__month=m_month, status='COMPLETED')
        sales_val = float(sales_m.aggregate(Sum('grand_total'))['grand_total__sum'] or 0.00)
        gross_p = sum(s.calculate_profit() for s in sales_m)
        
        expenses_m = float(Expense.objects.filter(expense_date__year=m_year, expense_date__month=m_month).aggregate(Sum('amount'))['amount__sum'] or 0.00)
        net_p = gross_p - expenses_m

        monthly_sales_data.append(sales_val)
        monthly_profit_data.append(net_p)

    return JsonResponse({
        'daily': {
            'labels': days_labels,
            'sales': daily_sales_data,
            'purchases': daily_purchases_data,
        },
        'monthly': {
            'labels': months_labels,
            'sales': monthly_sales_data,
            'profit': monthly_profit_data,
        }
    })
