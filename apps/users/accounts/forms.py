from django import forms
from phonenumber_field.validators import validate_phonenumber
from phonenumber_field.formfields import PhoneNumberField

class UserLoginForm(forms.Form):
    phone_number = PhoneNumberField(
        validators=[validate_phonenumber],
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "loginEmail",
                # "dir": "rtl",

            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "id": "loginPassword",
            }
        )
    )
