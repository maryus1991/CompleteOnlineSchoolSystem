from django import forms
from .models import Contact, Counseling

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('full_name', 'phone_number', 'message')
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    "id":"name"
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    "id":"phone",
                    "type":"tel",
                    "dir":"rtl",
                }
            ),
        }

class CounselingForm(forms.ModelForm):
    class Meta:
        model = Counseling
        fields = ('full_name', 'phone_number', 'message')
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    "id":"name"
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    "id":"phone",
                    "type":"tel",
                    "dir":"rtl",
                }
            ),
        }
