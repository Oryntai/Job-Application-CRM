from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .selectors import get_dashboard_snapshot, get_funnel_stats, get_source_stats, get_time_in_stage


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_dashboard_snapshot(self.request.user))
        context["funnel"] = get_funnel_stats(self.request.user)
        context["time_in_stage"] = get_time_in_stage(self.request.user)
        context["source_stats"] = get_source_stats(self.request.user)
        return context
