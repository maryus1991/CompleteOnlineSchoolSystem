from django.views.generic import TemplateView
from apps.users.students.mixins import StudentMixin

class MainStudentDashboardView(StudentMixin, TemplateView):
    """student dashboard view"""

    template_name = 'dashboard/main.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        return data

class EditAccountView(StudentMixin, TemplateView):
    """edit account dashboard view"""

    template_name = 'dashboard/account/account.html'

