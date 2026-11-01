
from apps.users.students.models import Student
from apps.users.advisers.models import Adviser

from apps.users.teachers.models import Teacher


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from apps.users.accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'PhoneNumber',
        'get_full_name',
        'type_of_user',
        'gender',
        'is_staff',
        'is_active',
        'is_verified',
        'sort_number',
    )

    list_filter = (
        'type_of_user',
        'gender',
        'is_staff',
        'is_active',
        'is_verified',
        'publish',
        'is_superuser',
    )

    search_fields = (
        'PhoneNumber',
        'first_name',
        'last_name',
        'email',
    )

    ordering = ('-sort_number', '-pk')


    fieldsets = (
        (None, {
            'fields': ('PhoneNumber', 'password')
        }),
        (_('اطلاعات شخصی'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'gender',
                'type_of_user',
                'profile_image',
                'biography',
                'telegram_link',
                'instagram_link',
            )
        }),
        (_('وضعیت حساب'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_verified',
                'publish',
                'sort_number',
            )
        }),
        (_('دسترسی‌ها'), {
            'fields': ('groups', 'user_permissions'),
        }),
        (_('تاریخ‌های مهم'), {
            'fields': ('last_login', 'date_joined'),
        }),
        (_('اطلاعات سیستمی'), {
            'classes': ('collapse',),
            'fields': (
                'otp',
                'otp_expiry_date',
                'login_temp',
                'private_code',
            ),
        }),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'PhoneNumber',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'type_of_user',
                'gender',
                'is_staff',
                'is_active',
            ),
        }),
    )


    readonly_fields = ('last_login', 'date_joined', 'otp', 'otp_expiry_date', 'login_temp')

    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(Student)
admin.site.register(Adviser)

admin.site.register(Teacher)