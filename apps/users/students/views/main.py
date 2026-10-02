

from django.views.generic import TemplateView
from apps.users.students.mixins import StudentMixin
from apps.users.students.forms.auth import StudentForm

class MainStudentDashboardView(StudentMixin, TemplateView):
    """student dashboard view"""

    template_name = 'dashboard/main.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        return data

class EditAccountView(StudentMixin, TemplateView):
    """edit account dashboard view"""

    template_name = 'dashboard/account/account.html'


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({
            "form": StudentForm(initial={
                "grade": self.request.student.grade or None ,
                "major": self.request.student.major or None ,
                "province": self.request.student.province or None ,
                "city": self.request.student.city or None ,
                "school": self.request.student.school or None ,
                "gender": self.request.user.gender or None,
                "PhoneNumber": self.request.user.PhoneNumber or None,
                "profile_image": self.request.user.profile_image or None,
                "biography": self.request.user.biography or None,
                "parent_phone_number":  self.request.student.parent_phone_number or None,
                "telegram_link": self.request.user.telegram_link or None,
                "instagram_link": self.request.user.instagram_link or None,
                "first_name": self.request.user.first_name or None,
                "last_name": self.request.user.last_name or None,
                "email": self.request.user.email or None,
            }),
        })
        return data