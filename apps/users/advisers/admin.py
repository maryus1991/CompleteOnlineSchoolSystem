from django.contrib import admin
from apps.users.advisers.models import Adviser

if admin.site.is_registered(Adviser):
    admin.site.unregister(Adviser)


@admin.register(Adviser)
class AdviserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "specialization",
        "school",
        "province",
        "city",
        "max_students_capacity",
        "can_manage_study_plans",
        "can_view_student_reports",
        "can_manage_sessions",
        "can_start_live_session",
        "can_answer_counseling_requests",
        "is_active",
    )
    list_filter = (
        "is_active",
        "school",
        "province",
        "can_manage_study_plans",
        "can_view_student_reports",
        "can_manage_sessions",
        "can_start_live_session",
        "can_answer_counseling_requests",
        "can_send_adviser_notes",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__PhoneNumber",
        "specialization",
        "province",
        "city",
    )
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user", "school")
