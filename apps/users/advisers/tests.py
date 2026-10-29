from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from apps.exams.models import Exam
from apps.progress.models import DailyStudyLog, StudyPlan
from apps.reports.models import ExamReport
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student


class AdviserIsolationAndCapacityTests(TestCase):
    def setUp(self):
        # Adviser A (max capacity = 1)
        self.user_a = User.objects.create(
            PhoneNumber="+989125551111",
            first_name="مشاور",
            last_name="الف",
            type_of_user=User.TypeOfUser.ADVISER,
            is_active=True,
        )
        self.adviser_a = Adviser.objects.create(
            user=self.user_a,
            max_students_capacity=1,
            is_active=True,
        )

        # Adviser B
        self.user_b = User.objects.create(
            PhoneNumber="+989125552222",
            first_name="مشاور",
            last_name="ب",
            type_of_user=User.TypeOfUser.ADVISER,
            is_active=True,
        )
        self.adviser_b = Adviser.objects.create(
            user=self.user_b,
            max_students_capacity=5,
            is_active=True,
        )

        # Student belonging to Adviser A
        self.st_user_1 = User.objects.create(
            PhoneNumber="+989125553333",
            first_name="دانش‌آموز",
            last_name="اول",
            type_of_user=User.TypeOfUser.STUDENT,
            is_active=True,
        )
        self.student_1 = Student.objects.create(
            user=self.st_user_1,
            adviser=self.adviser_a,
            is_active=True,
        )

    def test_data_isolation_between_advisers(self):
        """تست ۵ (الف): مشاور ب نباید به پرونده ۳۶۰، برنامه، گزارش کار یا کارنامه دانش‌آموز مشاور الف دسترسی داشته باشد"""
        plan = StudyPlan.objects.create(
            adviser=self.adviser_a,
            student=self.student_1,
            title="برنامه اختصاصی مشاور الف",
            start_date=now(),
            end_date=now(),
        )
        log = DailyStudyLog.objects.create(
            student=self.student_1,
            log_date=now(),
            actual_duration_minutes=60,
        )
        exam = Exam.objects.create(
            name="آزمون اختصاصی",
            start_at=now(),
            stop_at=now(),
            last_enter=now(),
        )
        report = ExamReport.objects.create(
            exam=exam,
            student=self.student_1,
            status=ExamReport.ReportStatus.PUBLISHED,
            percentage=80.0,
        )

        # Login as Adviser B
        self.client.force_login(self.user_b)

        # 1. Student 360 profile -> 404
        res_360 = self.client.get(
            reverse("adviser:student-detail", kwargs={"pk": self.student_1.pk})
        )
        self.assertEqual(res_360.status_code, 404)

        # 2. StudyPlan update -> 404
        res_plan = self.client.get(
            reverse("adviser:plan-update", kwargs={"pk": plan.pk})
        )
        self.assertEqual(res_plan.status_code, 404)

        # 3. DailyLog review -> 404
        res_log = self.client.post(
            reverse("adviser:daily-log-review", kwargs={"pk": log.pk}),
            data={"review_status": DailyStudyLog.ReviewStatus.APPROVED},
        )
        self.assertEqual(res_log.status_code, 404)

        # 4. ExamReport prescription -> 404
        res_presc = self.client.get(
            reverse("adviser:prescription-create", kwargs={"report_pk": report.pk})
        )
        self.assertEqual(res_presc.status_code, 404)

    def test_adviser_max_students_capacity_validation(self):
        """تست ۵ (ب): بررسی محدودیت ظرفیت مشاور در متد clean مدل Student"""
        self.assertEqual(self.adviser_a.active_students_count(), 1)
        self.assertEqual(self.adviser_a.remaining_capacity(), 0)

        st_user_2 = User.objects.create(
            PhoneNumber="+989125554444",
            first_name="دانش‌آموز",
            last_name="دوم",
            type_of_user=User.TypeOfUser.STUDENT,
            is_active=True,
        )
        student_2 = Student(
            user=st_user_2,
            adviser=self.adviser_a,
            is_active=True,
        )
        with self.assertRaises(ValidationError):
            student_2.clean()

    def test_all_adviser_and_student_counseling_pages_render_200(self):
        """تست ۶: بررسی رندر شدن بدون خطای تمامی صفحات پنل مشاور و بخش مشاوره دانش‌آموز (HTTP 200)"""
        self.adviser_a.can_answer_counseling_requests = True
        self.adviser_a.save(update_fields=["can_answer_counseling_requests"])

        self.client.force_login(self.user_a)
        adviser_urls = [
            reverse("adviser:main"),
            reverse("adviser:account"),
            reverse("adviser:student-list"),
            reverse("adviser:student-detail", kwargs={"pk": self.student_1.pk}),
            reverse("adviser:plan-list"),
            reverse("adviser:plan-create"),
            reverse("adviser:daily-log-list"),
            reverse("adviser:report-list"),
            reverse("adviser:session-list"),
            reverse("adviser:session-create"),
            reverse("adviser:site-requests"),
            reverse("adviser:ticket-list"),
            reverse("adviser:ticket-create"),
        ]
        for url in adviser_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Failed rendering adviser URL: {url}")

        self.client.force_login(self.st_user_1)
        student_urls = [
            reverse("student:counseling-hub"),
            reverse("student:counseling-plan-list"),
            reverse("student:counseling-daily-logs"),
            reverse("student:counseling-sessions"),
        ]
        for url in student_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Failed rendering student URL: {url}")
