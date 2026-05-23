import datetime

from multiprocessing.connection import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from apps.clients.models import Client
from django.contrib.auth.models import User
from .models import Task
from .forms import TaskForm
from .services import parse_task_with_ollama
from django.contrib import messages
from .services import generate_workspace_brief

User = get_user_model()
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/list.html"
    context_object_name = "tasks"
    # REMOVED: paginate_by = 20 (DataTables handles this on the client side now!)

    def get_queryset(self):
        # 1. Start by fetching ALL tasks from the database
        qs = Task.objects.all()
        
        # 2. OPTIMIZATION: Join 'assigned_to' and 'client' tables in 1 query instead of N+1 queries.
        # This keeps your avatar images and client dropdowns rendering instantly!
        qs = qs.select_related('assigned_to', 'client')
        
        # 3. OPTIONAL: If you want admins to see everything, but normal users to only see their own tasks:
        if not self.request.user.is_staff:
            qs = qs.filter(assigned_to=self.request.user)
        
        # Keep your URL status query filter operational
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
            
        return qs
    
class TaskCompleteView(LoginRequiredMixin, View):
    """Handles marking a task as complete using class-based routing."""
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs.get('pk'))
        task.status = 'done'
        task.save()
        # Redirect back to the previous screen, or fall back to the task list view
        return redirect(request.META.get('HTTP_REFERER', 'tasks:list'))

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"
    success_url = reverse_lazy("tasks:list")

    # ✅ ADD THIS: Delivers the current user logged into the browser to the form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Automatically sets the creator/assignee if left blank in your template form layout
        if not form.cleaned_data.get('assigned_to'):
            form.instance.assigned_to = self.request.user
        return super().form_valid(form)
    
    def get_queryset(self):
        # ✅ Filter out deactivated clients from the main dashboard data table
        return Client.objects.filter(is_active=True)

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"
    success_url = reverse_lazy("tasks:list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/confirm_delete.html"
    success_url = reverse_lazy("tasks:list")

class TaskQuickAddView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        command = request.POST.get('ai_command', '').strip()
        
        if not command:
            return redirect('tasks:list')
            
        ai_data = parse_task_with_ollama(command)
        
        # Fallback check if Ollama completely fails to parse anything
        if not ai_data or 'title' not in ai_data:
            messages.error(request, "AI was unable to comprehend the command layout structure.")
            return redirect('tasks:list')

        title = ai_data.get('title')
        priority = ai_data.get('priority', 'medium').lower()
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'

        # ---------------------------------------------------------------------
        # 🛡️ ROLE-BASED USER VALIDATION
        # ---------------------------------------------------------------------
        assigned_user = None
        raw_username = ai_data.get('assigned_to')

        if request.user.is_staff:
            # 👑 ADMIN FLOW: Explicitly requires a valid user match if typed
            if raw_username:
                matched_user = User.objects.filter(username__iexact=raw_username).first()
                if not matched_user:
                    messages.error(request, f"User Not Found: The profile identifier '{raw_username}' does not exist.")
                    return redirect('tasks:list')
                assigned_user = matched_user
            else:
                # No user typed by admin -> trigger error modal requirement
                messages.error(request, "User Not Found: Admin commands must explicitly specify an execution assignee target.")
                return redirect('tasks:list')
        else:
            # 👤 REGULAR USER FLOW: Default to current user session directly
            assigned_user = request.user

        # ---------------------------------------------------------------------
        # 🛡️ GLOBAL CLIENT VALIDATION (Applies to both roles)
        # ---------------------------------------------------------------------
        assigned_client = None
        raw_client_name = ai_data.get('client')

        if raw_client_name:
            matched_client = Client.objects.filter(name__icontains=raw_client_name).first()
            if not matched_client:
                messages.error(request, f"Client Not Found: '{raw_client_name}' does not match records.")
                return redirect('tasks:list')
            assigned_client = matched_client
        else:
            # No client signature was found or provided in the text string
            messages.error(request, "Client Not Found: Command execution rejected. This ecosystem requires explicit client assignment parameter structures.")
            return redirect('tasks:list')

        # ---------------------------------------------------------------------
        # 📅 DATE STAMP RESOLUTION & DATABASE WRITE
        # ---------------------------------------------------------------------
        computed_due_date = None
        raw_date_string = ai_data.get('due_date')
        if raw_date_string:
            try:
                computed_due_date = datetime.datetime.strptime(raw_date_string, "%Y-%m-%d").date()
            except ValueError:
                computed_due_date = None

        # 💡 Build a beautiful, structured HTML description instead of raw text
        rich_description = (command)

        # Safe creation guarantee point reached safely
        Task.objects.create(
            title=title,
            status='open',
            priority=priority,
            assigned_to=assigned_user,
            client=assigned_client,
            due_date=computed_due_date,
            description=rich_description
        )
        
        messages.success(request, f"Task '{title}' generated successfully via AI context engine.")
        return redirect('tasks:list')

class RegenerateBriefingView(LoginRequiredMixin, View):
    """Gathers user tasks, calls Ollama, and caches the updated AI briefing inside the user's session."""
    def post(self, request, *args, **kwargs):

        # 👑 ADMIN FLOW: Sees everything across the ecosystem
        if request.user.is_staff:
            open_tasks = Task.objects.filter(status='open').select_related('client', 'assigned_to')
            user_role = "Administrator"
        
        # 👤 REGULAR USER FLOW: Only sees their own work
        else:
            open_tasks = Task.objects.filter(assigned_to=request.user,status='open').select_related('client')
            user_role = "Team Member"

        # 2. Trigger the AI summary generator
        brief_html = generate_workspace_brief(
            user_name=request.user.first_name or request.user.username, 
            tasks_list=open_tasks,
            is_admin=request.user.is_staff
        )
        
        # 3. Store the markup inside session storage
        request.session['ai_workspace_brief'] = brief_html
        request.session.modified = True
        
        messages.success(request, "AI Copilot successfully updated your daily brief!")
        return redirect('tasks:list')
