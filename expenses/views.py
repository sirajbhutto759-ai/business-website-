import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm
from accounts.decorators import admin_required

@login_required
def expense_list(request):
    category_id = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    filter_type = request.GET.get('filter_type', 'month')

    today = datetime.date.today()
    expenses = Expense.objects.select_related('category', 'created_by').all()

    if filter_type == 'today':
        expenses = expenses.filter(expense_date=today)
    elif filter_type == 'month':
        expenses = expenses.filter(expense_date__year=today.year, expense_date__month=today.month)
    elif filter_type == 'year':
        expenses = expenses.filter(expense_date__year=today.year)
    elif filter_type == 'custom':
        if date_from:
            expenses = expenses.filter(expense_date__gte=date_from)
        if date_to:
            expenses = expenses.filter(expense_date__lte=date_to)

    if category_id:
        expenses = expenses.filter(category_id=category_id)

    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00
    categories = ExpenseCategory.objects.all()

    context = {
        'expenses': expenses,
        'categories': categories,
        'total_amount': total_amount,
        'selected_category': category_id,
        'filter_type': filter_type,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'expenses/expense_list.html', context)


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, f"Expense of Rs. {expense.amount} under '{expense.category.name}' logged successfully!")
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(initial={'expense_date': datetime.date.today()})
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add New Expense'})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f"Expense #{expense.id} updated successfully!")
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': f'Edit Expense #{expense.id}'})


@login_required
@admin_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense record deleted successfully.")
        return redirect('expenses:expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def category_list(request):
    categories = ExpenseCategory.objects.all()
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense category added successfully!")
            return redirect('expenses:category_list')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expenses/category_list.html', {'categories': categories, 'form': form})
