from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from apps.categories.models import LessonCategories
from apps.exams.models import Exam
from apps.progress.models import (
    AdviserExamPrescription,
    CounselingSession,
    DailyStudyLog,
    StudyPlan,
    StudyPlanItem,
)
from apps.reports.models import ExamReport
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student


class CounselingBidirectionalFlowTests(TestCase):
    def setUp(self):
        self.lesson = LessonCategories.objects.create(name="ریاضیات گسسته")

        # Adviser A
        self.adviser_user_a = User.objects.create(
            PhoneNumber="+989121111111",
            first_name="دکتر",
            last_name="مشاور اول",
            type_of_user=User.TypeOfUser.ADVISER,
            is_active=True,
        )
        self.adviser_a = Adviser.objects.create(
            user=self.adviser_user_a,
            specialization="مشاور کنکور ریاضی و تجربی",
            max_students_capacity=2,
            is_active=True,
        )

        # Adviser B (for Data Isolation test)
        self.adviser_user_b = User.objects.create(
            PhoneNumber="+989122222222",
            first_name="مهندس",
            last_name="مشاور دوم",
            type_of_user=User.TypeOfUser.ADVISER,
            is_active=True,
        )
        self.adviser_b = Adviser.objects.create(
            user=self.adviser_user_b,
            specialization="مشاور پایه",
            max_students_capacity=10,
            is_active=True,
        )

        # Student 1 under Adviser A
        self.student_user_1 = User.objects.create(
            PhoneNumber="+989123333333",
            first_name="امیر",
            last_name="دانش‌پژوه",
            type_of_user=User.TypeOfUser.STUDENT,
            is_active=True,
        )
        self.student_1 = Student.objects.create(
            user=self.student_user_1,
            adviser=self.adviser_a,
            target_major_rank="مهندسی کامپیوتر شریف - رتبه زیر ۱۰۰",
            is_active=True,
        )

    def test_1_adviser_creates_study_plan_and_items_and_student_toggles(self):
        """تست ۱ و ۲: ایجاد برنامه مطالعاتی توسط مشاور و تیک زدن باکس‌ها و ثبت گزارش کار توسط دانش‌آموز"""
        self.client.force_login(self.adviser_user_a)

        plan = StudyPlan.objects.create(
            adviser=self.adviser_a,
            student=self.student_1,
            title="برنامه هفته اول آبان",
            start_date=now(),
            end_date=now(),
            status=StudyPlan.Status.ACTIVE,
            adviser_description="<p>تمرکز ویژه روی تست‌های زمان‌دار</p>",
        )

        # Adviser adds item via StudyPlanItemsManageView formset
        resp = self.client.post(
            reverse("adviser:plan-items", kwargs={"pk": plan.pk}),
            data={
                "items-TOTAL_FORMS": "1",
                "items-INITIAL_FORMS": "0",
                "items-MIN_NUM_FORMS": "0",
                "items-MAX_NUM_FORMS": "1000",
                "items-0-day_of_week": str(StudyPlanItem.DayOfWeek.SATURDAY),
                "items-0-lesson": str(self.lesson.pk),
                "items-0-topic": "مبحث گراف و درخت",
                "items-0-study_type": StudyPlanItem.StudyType.TESTING,
                "items-0-target_duration_minutes": "90",
                "items-0-target_test_count": "40",
                "items-0-priority": StudyPlanItem.Priority.HIGH,
                "items-0-adviser_tip": "تست‌های مضرب ۳ زده شود",
                "items-0-sort_number": "1",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(plan.items.count(), 1)
        item = plan.items.first()
        self.assertEqual(plan.completion_percentage(), 0)

        # Switch to Student 1
        self.client.force_login(self.student_user_1)

        # Student views plan detail
        detail_resp = self.client.get(
            reverse("student:counseling-plan-detail", kwargs={"pk": plan.pk})
        )
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "مبحث گراف و درخت")

        # Student toggles item completion
        toggle_resp = self.client.post(
            reverse("student:counseling-plan-item-toggle", kwargs={"item_pk": item.pk})
        )
        self.assertEqual(toggle_resp.status_code, 302)
        item.refresh_from_db()
        self.assertTrue(item.is_completed_by_student)
        self.assertEqual(plan.completion_percentage(), 100)

        # Student submits a DailyStudyLog
        log_get_resp = self.client.get(reverse("student:counseling-daily-logs"))
        self.assertEqual(log_get_resp.status_code, 200)
        log_obj = DailyStudyLog.objects.create(
            student=self.student_1,
            study_plan_item=item,
            lesson=self.lesson,
            log_date=now(),
            actual_duration_minutes=95,
            tests_total=42,
            tests_correct=36,
            tests_wrong=6,
            focus_quality=DailyStudyLog.FocusQuality.FIVE,
            student_note="تمامی تست‌ها تحلیل شد.",
        )
        self.assertEqual(log_obj.review_status, DailyStudyLog.ReviewStatus.PENDING)

        # Adviser reviews and approves DailyStudyLog
        self.client.force_login(self.adviser_user_a)
        review_resp = self.client.post(
            reverse("adviser:daily-log-review", kwargs={"pk": log_obj.pk}),
            data={
                "review_status": DailyStudyLog.ReviewStatus.APPROVED,
                "adviser_feedback": "آفرین! دقتت در تست‌های گراف عالی بوده.",
            },
        )
        self.assertEqual(review_resp.status_code, 302)
        log_obj.refresh_from_db()
        self.assertEqual(log_obj.review_status, DailyStudyLog.ReviewStatus.APPROVED)
        self.assertIn("عالی", log_obj.adviser_feedback)

    def test_2_adviser_exam_prescription_and_student_reflection(self):
        """تست ۳: صدور نسخه مشاور روی کارنامه آزمون و ثبت تعهد توسط دانش‌آموز"""
        exam = Exam.objects.create(
            name="آزمون جامع مرحله اول",
            start_at=now(),
            stop_at=now(),
            last_enter=now(),
            lesson=self.lesson,
        )
        report = ExamReport.objects.create(
            exam=exam,
            student=self.student_1,
            status=ExamReport.ReportStatus.PUBLISHED,
            total_questions=50,
            correct_count=38,
            wrong_count=6,
            unanswered_count=6,
            percentage=72.0,
            answered_percentage=88.0,
            rank=14,
            published_at=now(),
        )

        # Adviser issues prescription
        self.client.force_login(self.adviser_user_a)
        presc_resp = self.client.post(
            reverse("adviser:prescription-create", kwargs={"report_pk": report.pk}),
            data={
                "strengths_analysis": "<p>تسلط عالی بر مباحث پایه</p>",
                "weaknesses_analysis": "<p>بی‌دقتی محاسباتی در ۱۰ دقیقه پایانی</p>",
                "action_plan_for_next_exam": "<p>اجرای تکنیک ضربدر و منها در منزل</p>",
            },
        )
        self.assertEqual(presc_resp.status_code, 302)
        prescription = AdviserExamPrescription.objects.get(exam_report=report)
        self.assertFalse(prescription.is_seen_by_student)

        # Student views report detail & prescription detail
        self.client.force_login(self.student_user_1)
        st_presc_get = self.client.get(
            reverse("student:counseling-prescription-detail", kwargs={"report_pk": report.pk})
        )
        self.assertEqual(st_presc_get.status_code, 200)
        prescription.refresh_from_db()
        self.assertTrue(prescription.is_seen_by_student)

        # Student submits reflection
        st_presc_post = self.client.post(
            reverse("student:counseling-prescription-detail", kwargs={"report_pk": report.pk}),
            data={"student_reflection": "متعهد می‌شوم تکنیک مدیریت زمان را در ۳ آزمون آزمایشی اجرا کنم."},
        )
        self.assertEqual(st_presc_post.status_code, 302)
        prescription.refresh_from_db()
        self.assertIn("متعهد", prescription.student_reflection)

    def test_3_counseling_session_request_and_adviser_approval(self):
        """تست ۴: درخواست جلسه مشاوره توسط دانش‌آموز و تایید و ثبت صورت‌جلسه توسط مشاور"""
        session = CounselingSession.objects.create(
            adviser=self.adviser_a,
            student=self.student_1,
            title="بررسی استراتژی جمع‌بندی",
            session_type=CounselingSession.SessionType.ONLINE_MEET,
            scheduled_at=now(),
            duration_minutes=45,
            status=CounselingSession.Status.REQUESTED_BY_STUDENT,
            student_request_note="نیاز به راهنمایی برای بودجه‌بندی آزمون بعدی دارم.",
        )
        self.assertEqual(session.status, CounselingSession.Status.REQUESTED_BY_STUDENT)

        # Adviser approves session and sets link & summary
        self.client.force_login(self.adviser_user_a)
        session.status = CounselingSession.Status.SCHEDULED
        session.meeting_link = "https://meet.example.com/room-101"
        session.session_summary = "<p>مصوب شد روزانه ۲ ساعت تست زمان‌دار کار شود.</p>"
        session.private_adviser_note = "یادداشت محرمانه مشاور: استرس دانش‌آموز کنترل شد."
        session.save()

        # Verify student sees summary but NOT private_adviser_note in template
        self.client.force_login(self.student_user_1)
        sess_resp = self.client.get(reverse("student:counseling-sessions"))
        self.assertEqual(sess_resp.status_code, 200)
        self.assertContains(sess_resp, "مصوب شد روزانه ۲ ساعت")
        self.assertNotContains(sess_resp, "یادداشت محرمانه مشاور: استرس")
