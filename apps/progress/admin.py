from django.contrib import admin
from apps.progress.models import (
    StudyPlan,
    StudyPlanItem,
    DailyStudyLog,
    AdviserExamPrescription,
    CounselingSession,
)


class StudyPlanItemInline(admin.TabularInline):
    model = StudyPlanItem
    extra = 1
    fields = (
        "day_of_week",
        "lesson",
        "topic",
        "study_type",
        "target_duration_minutes",
        "target_test_count",
        "priority",
        "is_completed_by_student",
        "sort_number",
    )


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "student",
        "adviser",
        "status",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("status", "is_active", "adviser")
    search_fields = (
        "title",
        "student__user__first_name",
        "student__user__last_name",
        "student__user__PhoneNumber",
        "adviser__user__first_name",
        "adviser__user__last_name",
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = [StudyPlanItemInline]


@admin.register(StudyPlanItem)
class StudyPlanItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "study_plan",
        "day_of_week",
        "lesson",
        "topic",
        "study_type",
        "target_duration_minutes",
        "target_test_count",
        "priority",
        "is_completed_by_student",
    )
    list_filter = (
        "day_of_week",
        "study_type",
        "priority",
        "is_completed_by_student",
        "lesson",
    )
    search_fields = ("topic", "study_plan__title", "adviser_tip")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DailyStudyLog)
class DailyStudyLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "lesson",
        "log_date",
        "actual_duration_minutes",
        "tests_total",
        "tests_correct",
        "tests_wrong",
        "focus_quality",
        "review_status",
    )
    list_filter = ("review_status", "focus_quality", "lesson", "is_active")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__PhoneNumber",
        "student_note",
        "adviser_feedback",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(AdviserExamPrescription)
class AdviserExamPrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exam_report",
        "student",
        "adviser",
        "is_seen_by_student",
        "created_at",
    )
    list_filter = ("is_seen_by_student", "adviser", "is_active")
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "exam_report__exam__name",
        "student_reflection",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "student",
        "adviser",
        "session_type",
        "scheduled_at",
        "duration_minutes",
        "status",
    )
    list_filter = ("status", "session_type", "adviser", "is_active")
    search_fields = (
        "title",
        "student__user__first_name",
        "student__user__last_name",
        "adviser__user__first_name",
        "adviser__user__last_name",
        "student_request_note",
    )
    readonly_fields = ("created_at", "updated_at")
