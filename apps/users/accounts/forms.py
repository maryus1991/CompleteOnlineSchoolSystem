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
                "placeholder": ""

            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "id": "loginPassword",
                "placeholder": ""

            }
        )
    )


class UserRegisterForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            "id": "regName",
            "placeholder": ""

        }),
    )

    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            "id": "regLastName",
            "placeholder": ""

        }),
    )

    phone_number = PhoneNumberField(
        validators=[validate_phonenumber],
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "regPhone",
                "placeholder": ""


            }
        )
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "id": "regPassword",
            "placeholder": ""

        }),
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "id": "regConfirmPassword",
            "placeholder": ""

        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "رمز عبور و تکرار آن یکسان نیستند")

        return cleaned_data
