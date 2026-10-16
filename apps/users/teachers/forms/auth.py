from django import forms
from django.core.validators import FileExtensionValidator
from apps.schools.models import School
from apps.users.accounts.models import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber


class TeacherForm(forms.Form):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": ""
            }
        )
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": ""
            }
        )
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": ""
            }
        )
    )

    province = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": ""
            }
        )
    )

    city = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": ""
            }
        )
    )

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(

        ),
        empty_label="انتخاب مدرسه"
    )

    gender = forms.ChoiceField(
        choices=User.GenderOfUser.choices,
        required=False,
        widget=forms.Select(
            attrs={
                "placeholder": ""
            }
        ),
    )

    PhoneNumber = PhoneNumberField(
        validators=[validate_phonenumber],
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "regPhone",
                "placeholder": ""
            }
        )
    )

    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "placeholder": ""
            }
        ),
        validators = [
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ]

    )
    biography = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": ""
            }
        )
    )

    telegram_link = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": ""
            }
        )
    )
    instagram_link = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": ""
            }
        )
    )
    last_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": ""
            }
        ),
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": ""
            }
        ),
    )
    conform_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": ""
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if not password or not confirm_password:
                self.add_error(
                    "confirm_password",
                    "برای تغییر رمز، رمز جدید و تکرار آن را وارد کنید",
                )
            elif password != confirm_password:
                self.add_error(
                    "confirm_password",
                    "رمز عبور و تکرار آن یکسان نیستند",
                )

        return cleaned_data
