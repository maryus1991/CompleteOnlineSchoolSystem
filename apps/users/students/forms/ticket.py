from django import forms

from .models import Ticket


class TicketCreateForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = [
            "name",
            "description",
            "file",
            "priority",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-group-glass",
                    "placeholder": "موضوع تیکت را وارد کنید",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-group-glass",
                    "placeholder": "توضیحات درخواست خود را بنویسید...",
                    "rows": 7,
                }
            ),

            "file": forms.FileInput(
                attrs={
                    "class": "form-group-glass",
                }
            ),

            "priority": forms.Select(
                attrs={
                    "class": "form-group-glass",
                }
            ),
        }