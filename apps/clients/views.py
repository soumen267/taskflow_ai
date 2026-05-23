from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Client  
from .forms import ClientForm
from django.shortcuts import get_object_or_404, redirect
from django.views import View


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "clients/list.html"
    context_object_name = "clients"
    paginate_by = 20

    def get_queryset(self):
        # qs = Client.objects.filter(assigned_to=self.request.user)
        # status = self.request.GET.get("status")
        # if status:
        #     qs = qs.filter(status=status)
        # return qs
        return Client.objects.filter(assigned_to=self.request.user)

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "clients/detail.html"
    context_object_name = "client"


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        form.instance.assigned_to = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client 
    form_class = ClientForm
    template_name = "clients/form.html"
    success_url = reverse_lazy("clients:list")


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "clients/confirm_delete.html"
    success_url = reverse_lazy("clients:list")
# FIXED: Changed from ListView to View

class ClientToggleActiveView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        # 1. Fetch the client safely
        client_to_toggle = get_object_or_404(Client, pk=pk)
        
        # Prevent admins from accidentally deactivating themselves!
        if client_to_toggle == request.user:
            return redirect("clients:list")
            
        # 2. Flip the active status
        client_to_toggle.is_active = not client_to_toggle.is_active
        client_to_toggle.save()
        
        # 3. Redirect back to the client dashboard list page
        return redirect("clients:list")