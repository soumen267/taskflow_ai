from apps.accounts.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import UserForm 
from django.shortcuts import get_object_or_404, redirect
from django.views import View # This is the class we want to use!


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "users/list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined")


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/detail.html"
    context_object_name = "user"


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users:list")


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User 
    form_class = UserForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users:list")


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/confirm_delete.html"
    success_url = reverse_lazy("users:list")


# FIXED: Changed from ListView to View
class UserToggleActiveView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        # 1. Fetch the user safely
        user_to_toggle = get_object_or_404(User, pk=pk)
        
        # Prevent admins from accidentally deactivating themselves!
        if user_to_toggle == request.user:
            return redirect("users:list")
            
        # 2. Flip the active status
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()
        
        # 3. Redirect back to the user dashboard list page
        return redirect("users:list")