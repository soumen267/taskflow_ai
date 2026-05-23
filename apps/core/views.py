from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from apps.tasks.models import Task
        user = self.request.user
        ctx["total_tasks"] = Task.objects.filter(assigned_to=user).count()
        ctx["open_tasks"] = Task.objects.filter(assigned_to=user, status="open").count()
        ctx["done_tasks"] = Task.objects.filter(assigned_to=user, status="done").count()
        ctx["recent_tasks"] = Task.objects.filter(assigned_to=user).order_by("-created_at")[:5]
        return ctx
