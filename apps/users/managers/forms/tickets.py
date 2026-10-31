from django import forms
from apps.ticket.models import Ticket
from apps.users.advisers.models import Adviser
from apps.users.teachers.models import Teacher


class ManagerTicketReplyForm(forms.Form):
    admin_message = forms.CharField(
        label="پاسخ مدیر مدرسه",
        required=True,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "متن پاسخ خود را بنویسید..."}
        ),
    )
    status = forms.ChoiceField(
        label="وضعیت تیکت پس از پاسخ",
        choices=Ticket.TicketStatus.choices,
        initial=Ticket.TicketStatus.awating_user,
        required=False,
    )


class ManagerTicketAssignForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "status",
            "priority",
            "assigned_teacher",
            "assigned_adviser",
            "is_active",
        ]

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        if school is not None:
            self.fields["assigned_teacher"].queryset = Teacher.objects.filter(
                school=school, is_active=True
            ).select_related("user")
            self.fields["assigned_adviser"].queryset = Adviser.objects.filter(
                school=school, is_active=True
            ).select_related("user")
