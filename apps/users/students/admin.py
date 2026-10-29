from django.contrib import admin
from apps.users.students.models import Student


if admin.site.is_registered(Student):
    admin.site.unregister(Student)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "grade",
        "major",
        "school",
        "adviser",
        "target_major_rank",
        "province",
        "city",
        "is_active",
    )
    list_filter = (
        "is_active",
        "grade",
        "major",
        "school",
        "adviser",
        "province",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__PhoneNumber",
        "parent_phone_number",
        "target_major_rank",
        "province",
        "city",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "adviser", "school")
