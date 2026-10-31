from django.urls import path
from apps.users.managers.views import (
    ManagerDashboardView,
    ManagerEditAccountView,
    StudentListView,
    StudentCreateView,
    StudentUpdateView,
    StudentToggleActiveView,
    StudentExcelTemplateDownloadView,
    StudentBulkImportView,
    TeacherListView,
    TeacherCreateView,
    TeacherUpdateView,
    TeacherPermissionsUpdateView,
    TeacherToggleActiveView,
    AdviserListView,
    AdviserCreateView,
    AdviserUpdateView,
    AdviserPermissionsUpdateView,
    AdviserToggleActiveView,
    SchoolInfoUpdateView,
    ClassListView,
    ClassCreateView,
    ClassUpdateView,
    ClassToggleActiveView,
    SectionManageView,
    SectionToggleActiveView,
    SectionContentToggleActiveView,
    ExamListView,
    ExamCreateView,
    ExamUpdateView,
    ExamStatusActionView,
    ExamAnalyticalDetailView,
    PracticeListView,
    PracticeCreateView,
    PracticeUpdateView,
    PracticeToggleActiveView,
    LiveClassListView,
    LiveClassCreateView,
    LiveClassUpdateView,
    LiveClassToggleActiveView,
    AdviserLiveSessionCreateView,
    StreamServerMonitorView,
    LiveRequestReviewView,
    TicketListView,
    TicketDetailView,
    TicketToggleActiveView,
    ManagerExamReportView,
    ManagerTeacherReportView,
    ManagerAdviserReportView,
    ManagerStudentReportView,
    ManagerStudentReportCardView,
    SchoolSettingsUpdateView,
    SchoolAnnouncementToggleActiveView,
    ManagerArticleListView,
    ManagerArticleCreateView,
    ManagerArticleUpdateView,
    ManagerArticleToggleActiveView,
)

app_name = "manager"

urlpatterns = [
    # ۱. داشبورد و حساب مدیر مدرسه
    path("main/", ManagerDashboardView.as_view(), name="main"),
    path("account/", ManagerEditAccountView.as_view(), name="account"),

    # ۲. مدیریت کاربران (دانش‌آموز، معلم، مشاور) + ایمپورت اکسل و مجوزها
    path("users/students/", StudentListView.as_view(), name="student-list"),
    path("users/students/create/", StudentCreateView.as_view(), name="student-create"),
    path("users/students/<int:pk>/edit/", StudentUpdateView.as_view(), name="student-edit"),
    path("users/students/<int:pk>/toggle-active/", StudentToggleActiveView.as_view(), name="student-toggle-active"),
    path("users/students/import/", StudentBulkImportView.as_view(), name="student-import"),
    path("users/students/import/template/", StudentExcelTemplateDownloadView.as_view(), name="student-import-template"),

    path("users/teachers/", TeacherListView.as_view(), name="teacher-list"),
    path("users/teachers/create/", TeacherCreateView.as_view(), name="teacher-create"),
    path("users/teachers/<int:pk>/edit/", TeacherUpdateView.as_view(), name="teacher-edit"),
    path("users/teachers/<int:pk>/permissions/", TeacherPermissionsUpdateView.as_view(), name="teacher-permissions"),
    path("users/teachers/<int:pk>/toggle-active/", TeacherToggleActiveView.as_view(), name="teacher-toggle-active"),

    path("users/advisers/", AdviserListView.as_view(), name="adviser-list"),
    path("users/advisers/create/", AdviserCreateView.as_view(), name="adviser-create"),
    path("users/advisers/<int:pk>/edit/", AdviserUpdateView.as_view(), name="adviser-edit"),
    path("users/advisers/<int:pk>/permissions/", AdviserPermissionsUpdateView.as_view(), name="adviser-permissions"),
    path("users/advisers/<int:pk>/toggle-active/", AdviserToggleActiveView.as_view(), name="adviser-toggle-active"),

    # ۳. مدیریت مدرسه، پایه‌ها/رشته‌ها/دروس، کلاس‌ها و جلسات
    path("school/", SchoolInfoUpdateView.as_view(), name="school-info"),
    path("classes/", ClassListView.as_view(), name="class-list"),
    path("classes/create/", ClassCreateView.as_view(), name="class-create"),
    path("classes/<int:pk>/edit/", ClassUpdateView.as_view(), name="class-edit"),
    path("classes/<int:pk>/toggle-active/", ClassToggleActiveView.as_view(), name="class-toggle-active"),
    path("classes/<int:class_pk>/sections/", SectionManageView.as_view(), name="class-sections"),
    path("sections/<int:pk>/toggle-active/", SectionToggleActiveView.as_view(), name="section-toggle-active"),
    path("sections/content/<str:kind>/<int:pk>/toggle-active/", SectionContentToggleActiveView.as_view(), name="section-content-toggle-active"),

    # ۴. مدیریت آزمون‌ها و تمرین‌ها
    path("exams/", ExamListView.as_view(), name="exam-list"),
    path("exams/create/", ExamCreateView.as_view(), name="exam-create"),
    path("exams/<int:pk>/edit/", ExamUpdateView.as_view(), name="exam-edit"),
    path("exams/<int:pk>/status/", ExamStatusActionView.as_view(), name="exam-status"),
    path("exams/<int:pk>/analytics/", ExamAnalyticalDetailView.as_view(), name="exam-analytics"),

    path("practices/", PracticeListView.as_view(), name="practice-list"),
    path("practices/create/", PracticeCreateView.as_view(), name="practice-create"),
    path("practices/<int:pk>/edit/", PracticeUpdateView.as_view(), name="practice-edit"),
    path("practices/<int:pk>/toggle-active/", PracticeToggleActiveView.as_view(), name="practice-toggle-active"),

    # ۵. مدیریت کلاس‌های آنلاین و مانیتورینگ سرورهای استریم مدرسه
    path("live-classes/", LiveClassListView.as_view(), name="live-list"),
    path("live-classes/create/", LiveClassCreateView.as_view(), name="live-create"),
    path("live-classes/<int:pk>/edit/", LiveClassUpdateView.as_view(), name="live-edit"),
    path("live-classes/<int:pk>/toggle-active/", LiveClassToggleActiveView.as_view(), name="live-toggle-active"),
    path("live-classes/adviser-session/create/", AdviserLiveSessionCreateView.as_view(), name="adviser-live-create"),
    path("live-classes/servers/", StreamServerMonitorView.as_view(), name="server-monitor"),
    path("live-classes/requests/<str:kind>/<int:pk>/review/", LiveRequestReviewView.as_view(), name="live-request-review"),

    # ۶. تیکت و پشتیبانی مدرسه
    path("tickets/", TicketListView.as_view(), name="ticket-list"),
    path("tickets/<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
    path("tickets/<int:pk>/toggle-active/", TicketToggleActiveView.as_view(), name="ticket-toggle-active"),

    # ۷. گزارش‌گیری پیشرفته و صدور کارنامه قابل پرینت A4 (سمت کاربر)
    path("reports/exams/", ManagerExamReportView.as_view(), name="report-exams"),
    path("reports/teachers/", ManagerTeacherReportView.as_view(), name="report-teachers"),
    path("reports/advisers/", ManagerAdviserReportView.as_view(), name="report-advisers"),
    path("reports/students/", ManagerStudentReportView.as_view(), name="report-students"),
    path("reports/report-cards/", ManagerStudentReportCardView.as_view(), name="report-cards"),

    # ۸. تنظیمات اختصاصی مدرسه و اعلان‌ها
    path("settings/", SchoolSettingsUpdateView.as_view(), name="school-settings"),
    path("settings/announcements/<int:pk>/toggle-active/", SchoolAnnouncementToggleActiveView.as_view(), name="announcement-toggle-active"),

    # ۹. مدیریت محتوا (مقالات عمومی و اختصاصی مدرسه)
    path("articles/", ManagerArticleListView.as_view(), name="article-list"),
    path("articles/create/", ManagerArticleCreateView.as_view(), name="article-create"),
    path("articles/<int:pk>/edit/", ManagerArticleUpdateView.as_view(), name="article-edit"),
    path("articles/<int:pk>/toggle-active/", ManagerArticleToggleActiveView.as_view(), name="article-toggle-active"),
]
