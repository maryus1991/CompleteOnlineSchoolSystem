from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField

from apps.categories.models import GradeCategories, MajorCategories
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher
from apps.users.managers.excel_utils import normalize_iran_phone, is_valid_iran_phone


class ManagerAccountForm(forms.Form):
    first_name = forms.CharField(label="نام", max_length=150, required=True)
    last_name = forms.CharField(label="نام خانوادگی", max_length=150, required=True)
    email = forms.EmailField(label="ایمیل", required=False)
    gender = forms.ChoiceField(label="جنسیت", choices=User.GenderOfUser.choices, required=True)
    province = forms.CharField(label="استان", max_length=255, required=False)
    city = forms.CharField(label="شهر", max_length=255, required=False)
    biography = forms.CharField(
        label="معرفی کوتاه",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    telegram_link = forms.URLField(label="لینک تلگرام", required=False)
    instagram_link = forms.URLField(label="لینک اینستاگرام", required=False)
    profile_image = forms.ImageField(label="تصویر پروفایل", required=False)

    last_password = forms.CharField(
        label=" رمز عبور فعلی (در صورت نیاز به تغییر رمز وارد شود)",
        required=False,
        widget=forms.PasswordInput(),
    )
    password = forms.CharField(
        label="  رمز عبور جدید (در صورت نیاز به تغییر رمز وارد شود)",
        required=False,
        widget=forms.PasswordInput(),
    )
    conform_password = forms.CharField(
        label=" تایید  رمز عبور جدید (در صورت نیاز به تغییر رمز وارد شود)",
        required=False,
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("conform_password") or cleaned_data.get("confirm_password")

        if password or confirm_password:
            if not password or not confirm_password:
                self.add_error(
                    "conform_password",
                    "برای تغییر رمز، رمز جدید و تکرار آن را وارد کنید",
                )
            elif password != confirm_password:
                self.add_error(
                    "conform_password",
                    "رمز عبور و تکرار آن یکسان نیستند",
                )
        return cleaned_data



class ManagerStudentForm(forms.Form):
    phone_number = forms.CharField(label="شماره موبایل", max_length=20, required=True)
    first_name = forms.CharField(label="نام", max_length=150, required=True)
    last_name = forms.CharField(label="نام خانوادگی", max_length=150, required=True)
    gender = forms.ChoiceField(label="جنسیت", choices=User.GenderOfUser.choices, required=True)
    private_code = forms.CharField(label="کد ملی / کد اختصاصی", max_length=100, required=False)
    parent_phone_number = forms.CharField(label="شماره والدین", max_length=20, required=False)
    grade = forms.ModelChoiceField(
        label="پایه تحصیلی",
        queryset=GradeCategories.objects.filter(is_active=True),
        required=False,
    )
    major = forms.ModelChoiceField(
        label="رشته تحصیلی",
        queryset=MajorCategories.objects.filter(is_active=True),
        required=False,
    )
    adviser = forms.ModelChoiceField(
        label="مشاور تحصیلی",
        queryset=Adviser.objects.none(),
        required=False,
    )
    province = forms.CharField(label="استان", max_length=255, required=False)
    city = forms.CharField(label="شهر", max_length=255, required=False)
    target_major_rank = forms.CharField(label="هدف تحصیلی / رشته و رتبه هدف", max_length=255, required=False)
    counseling_notes_summary = forms.CharField(
        label="پرونده و شناخت کلی مشاور",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    password = forms.CharField(
        label="رمز عبور (در ویرایش در صورت خالی بودن تغییر نمی‌کند)",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )
    is_active = forms.BooleanField(label="فعال", required=False, initial=True)

    def __init__(self, *args, school=None, student_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        self.student_instance = student_instance
        if school is not None:
            self.fields["adviser"].queryset = Adviser.objects.filter(
                school=school, is_active=True
            ).select_related("user")

    def clean_phone_number(self):
        raw = self.cleaned_data.get("phone_number", "")
        phone = normalize_iran_phone(raw)
        if not is_valid_iran_phone(phone):
            raise ValidationError("شماره موبایل معتبر نیست (فرمت صحیح: 0912xxxxxxx).")
        qs = User.objects.filter(PhoneNumber=phone)
        if self.student_instance and self.student_instance.user_id:
            qs = qs.exclude(pk=self.student_instance.user_id)
        if qs.exists():
            raise ValidationError("این شماره موبایل قبلاً در سامانه ثبت شده است.")
        return phone

    def clean_parent_phone_number(self):
        raw = (self.cleaned_data.get("parent_phone_number") or "").strip()
        if not raw:
            return None
        phone = normalize_iran_phone(raw)
        if not is_valid_iran_phone(phone):
            raise ValidationError("شماره والدین معتبر نیست.")
        return phone

    def clean_private_code(self):
        code = (self.cleaned_data.get("private_code") or "").strip()
        if not code:
            return None
        qs = User.objects.filter(private_code=code)
        if self.student_instance and self.student_instance.user_id:
            qs = qs.exclude(pk=self.student_instance.user_id)
        if qs.exists():
            raise ValidationError("این کد ملی / کد اختصاصی قبلاً برای کاربر دیگری ثبت شده است.")
        return code


class StudentBulkImportForm(forms.Form):
    file = forms.FileField(
        label="فایل اکسل (.xlsx) یا CSV دانش‌آموزان",
        required=True,
        help_text="فایل قالب استاندارد را دانلود و تکمیل نمایید.",
    )
    default_adviser = forms.ModelChoiceField(
        label="اختصاص خودکار به مشاور مدرسه (اختیاری)",
        queryset=Adviser.objects.none(),
        required=False,
    )

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school is not None:
            self.fields["default_adviser"].queryset = Adviser.objects.filter(
                school=school, is_active=True
            ).select_related("user")


class ManagerTeacherForm(forms.Form):
    phone_number = forms.CharField(label="شماره موبایل", max_length=20, required=True)
    first_name = forms.CharField(label="نام", max_length=150, required=True)
    last_name = forms.CharField(label="نام خانوادگی", max_length=150, required=True)
    email = forms.EmailField(label="ایمیل", required=False)
    gender = forms.ChoiceField(label="جنسیت", choices=User.GenderOfUser.choices, required=True)
    private_code = forms.CharField(label="کد ملی / کد اختصاصی", max_length=100, required=False)
    province = forms.CharField(label="استان", max_length=255, required=False)
    city = forms.CharField(label="شهر", max_length=255, required=False)
    biography = forms.CharField(
        label="معرفی کوتاه و سوابق تدریس",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    password = forms.CharField(
        label="رمز عبور",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )
    is_active = forms.BooleanField(label="فعال", required=False, initial=True)

    def __init__(self, *args, teacher_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_instance = teacher_instance

    def clean_phone_number(self):
        raw = self.cleaned_data.get("phone_number", "")
        phone = normalize_iran_phone(raw)
        if not is_valid_iran_phone(phone):
            raise ValidationError("شماره موبایل معتبر نیست (فرمت صحیح: 0912xxxxxxx).")
        qs = User.objects.filter(PhoneNumber=phone)
        if self.teacher_instance and self.teacher_instance.user_id:
            qs = qs.exclude(pk=self.teacher_instance.user_id)
        if qs.exists():
            raise ValidationError("این شماره موبایل قبلاً در سامانه ثبت شده است.")
        return phone


class TeacherPermissionsForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "can_add_exam",
            "can_add_practice",

            "can_add_question",
            "can_add_class_section",
            "can_add_class_article",
            "can_add_class_file",
            "can_start_live_class",
            "can_issuing_report",

            "can_change_account",
        ]


class ManagerAdviserForm(forms.Form):
    phone_number = forms.CharField(label="شماره موبایل", max_length=20, required=True)
    first_name = forms.CharField(label="نام", max_length=150, required=True)
    last_name = forms.CharField(label="نام خانوادگی", max_length=150, required=True)
    email = forms.EmailField(label="ایمیل", required=False)
    gender = forms.ChoiceField(label="جنسیت", choices=User.GenderOfUser.choices, required=True)
    private_code = forms.CharField(label="کد ملی / کد اختصاصی", max_length=100, required=False)
    specialization = forms.CharField(label="تخصص مشاوره‌ای", max_length=255, required=False)
    max_students_capacity = forms.IntegerField(
        label="حداکثر ظرفیت دانش‌آموز",
        min_value=1,
        max_value=2000,
        initial=50,
        required=True,
    )
    province = forms.CharField(label="استان", max_length=255, required=False)
    city = forms.CharField(label="شهر", max_length=255, required=False)
    biography = forms.CharField(
        label="معرفی کوتاه مشاور",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    password = forms.CharField(
        label="رمز عبور",
        required=False,
        widget=forms.PasswordInput(render_value=False),
    )
    is_active = forms.BooleanField(label="فعال", required=False, initial=True)

    def __init__(self, *args, adviser_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.adviser_instance = adviser_instance

    def clean_phone_number(self):
        raw = self.cleaned_data.get("phone_number", "")
        phone = normalize_iran_phone(raw)
        if not is_valid_iran_phone(phone):
            raise ValidationError("شماره موبایل معتبر نیست (فرمت صحیح: 0912xxxxxxx).")
        qs = User.objects.filter(PhoneNumber=phone)
        if self.adviser_instance and self.adviser_instance.user_id:
            qs = qs.exclude(pk=self.adviser_instance.user_id)
        if qs.exists():
            raise ValidationError("این شماره موبایل قبلاً در سامانه ثبت شده است.")
        return phone


class AdviserPermissionsForm(forms.ModelForm):
    class Meta:
        model = Adviser
        fields = [
            "max_students_capacity",
            "can_manage_study_plans",
            "can_view_student_reports",
            "can_manage_sessions",
            "can_start_live_session",

            "can_send_adviser_notes",
            "can_change_account",
        ]
