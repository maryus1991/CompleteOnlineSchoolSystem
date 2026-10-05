from django import forms
from django.core.validators import FileExtensionValidator

from .models import Ticket


class TicketCreateForm(forms.ModelForm):
    file= forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "form-group-glass",
            },
        ),
        validators=[FileExtensionValidator(["pdf", "zip", "rar", "png", "jpg", "jpeg"])],
    )

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
            "priority": forms.Select(
                attrs={
                    "class": "form-group-glass",
                }
            ),
        }