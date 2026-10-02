from django import forms
from django.core.validators import FileExtensionValidator
from apps.categories.models import GradeCategories, MajorCategories, ProvinceCategories, CityCategories
from apps.schools.models import School
from apps.users.accounts.models import User
from phonenumber_field.formfields import PhoneNumberField


class StudentForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput()
    )
    grade = forms.ModelChoiceField(
        queryset=GradeCategories.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(),
        empty_label="انتخاب پایه"

    )

    major = forms.ModelChoiceField(
        queryset=MajorCategories.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(),
        empty_label="انتخاب رشته"

    )

    province = forms.ModelChoiceField(
        queryset=ProvinceCategories.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(),
        empty_label="انتخاب استان"
    )

    city = forms.ModelChoiceField(
        queryset=CityCategories.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(),
        empty_label="انتخاب شهر"
    )

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(),
        empty_label="انتخاب مدرسه"
    )

    gender = forms.ChoiceField(
        choices=User.GenderOfUser.choices,
        required=True,
        widget=forms.Select(),
    )

    PhoneNumber = PhoneNumberField(
        required=True
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(),
        validators = [
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ]

    )
    biography = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )
    parent_phone_number = PhoneNumberField(
        required=True,
        widget=forms.TelInput()
    )
    telegram_link = forms.URLField(
        required=False,
        widget=forms.URLInput()
    )
    instagram_link = forms.URLField(
        required=False,
        widget=forms.URLInput()
    )
    last_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
    )
    conform_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
    )

