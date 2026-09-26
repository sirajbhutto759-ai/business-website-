import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import ServiceJob
from .forms import ServiceJobForm
from customers.models import Customer
from accounts.decorators import admin_required

@login_required
def service_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    service_type = request.GET.get('service_type', '')

    services = ServiceJob.objects.select_related('customer', 'created_by').all()

    if query:
        services = services.filter(
            Q(service_no__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_phone__icontains=query) |
            Q(description__icontains=query)
        )

    if status:
        services = services.filter(status=status)

    if service_type:
        services = services.filter(service_type=service_type)

    return render(request, 'services/service_list.html', {
        'services': services,
        'query': query,
        'selected_status': status,
        'selected_type': service_type,
    })


@login_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceJobForm(request.POST)
        if form.is_valid():
            srv = form.save(commit=False)
            srv.service_no = ServiceJob.generate_service_no()
            srv.total_charges = srv.labor_charges + srv.material_charges
            srv.remaining_balance = max(0.00, float(srv.total_charges) - float(srv.paid_amount))
            srv.created_by = request.user
            srv.save()
            messages.success(request, f"Service Job #{srv.service_no} created successfully!")
            return redirect('services:service_detail', pk=srv.pk)
    else:
        form = ServiceJobForm(initial={
            'service_date': datetime.date.today(),
            'status': 'PENDING'
        })
    next_service_no = ServiceJob.generate_service_no()
    return render(request, 'services/service_form.html', {
        'form': form,
        'next_service_no': next_service_no,
        'title': 'Create New Service / Repair Ticket'
    })


@login_required
def service_detail(request, pk):
    service = get_object_or_404(ServiceJob.objects.select_related('customer', 'created_by'), pk=pk)
    return render(request, 'services/service_detail.html', {'service': service})


@login_required
def service_edit(request, pk):
    service = get_object_or_404(ServiceJob, pk=pk)
    if request.method == 'POST':
        form = ServiceJobForm(request.POST, instance=service)
        if form.is_valid():
            srv = form.save(commit=False)
            srv.total_charges = srv.labor_charges + srv.material_charges
            srv.remaining_balance = max(0.00, float(srv.total_charges) - float(srv.paid_amount))
            if srv.status in ['COMPLETED', 'DELIVERED'] and not srv.completion_date:
                srv.completion_date = datetime.date.today()
            srv.save()
            messages.success(request, f"Service Job #{srv.service_no} updated successfully!")
            return redirect('services:service_detail', pk=srv.pk)
    else:
        form = ServiceJobForm(instance=service)
    return render(request, 'services/service_form.html', {
        'form': form,
        'service': service,
        'title': f'Edit Service Job: {service.service_no}'
    })


@login_required
@admin_required
def service_delete(request, pk):
    service = get_object_or_404(ServiceJob, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, f"Service Job #{service.service_no} deleted.")
        return redirect('services:service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})
