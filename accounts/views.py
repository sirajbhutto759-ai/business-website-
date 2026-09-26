from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from .forms import UserCreateForm, UserEditForm
from .decorators import admin_required

class CustomLoginView(DjangoLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return super().get_success_url()

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')

@login_required
@admin_required
def user_list(request):
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User '{user.username}' created successfully!")
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create New User'})

@login_required
@admin_required
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user_obj.username}' updated successfully!")
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=user_obj)
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'Edit User: {user_obj.username}'})

@login_required
@admin_required
def user_toggle_status(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:user_list')
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    status_str = "activated" if user_obj.is_active else "deactivated"
    messages.success(request, f"User '{user_obj.username}' has been {status_str}.")
    return redirect('accounts:user_list')
