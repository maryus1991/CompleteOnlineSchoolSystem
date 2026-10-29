from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.common.utils import datetime2jalali
from apps.live_classes.models import (
    AdviserLiveSession,
    AdviserLiveSessionReport,
    AdviserLiveSessionRequest,
    StreamServers,
)
from apps.progress.models import CounselingSession
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class AdviserLiveSessionTests(TestCase):
    def setUp(self):
        self.server = StreamServers.objects.create(
            name="سرور اصلی مشاوره",
            base_url="https://stream.school.ir",
            server_stats_check="/monitor/stats",
            teacher_url_name="/teacher.html",
            TEACHER_KEY="SECRET_ADVISER_KEY",
            student_url_name="/student.html",
            MONITOR_TOKEN="MON_TOKEN",
            is_active=True,
        )

        # مشاور الف
        self.user_a = User.objects.create(
            PhoneNumber="+989123001001",
            first_name="دکتر",
            last_name="مشاور الف",
            type_of_user=User.TypeOfUser.ADVISER,
            is_active=True,
            is_verified=True,
        )
        self.adviser_a = Adviser.objects.create(
            user=self.user_a,
            specialization="مشاور کنکور تجربی",
            can_start_live_session=True,
            is_active=True,
        )

        # مشاور ب
        self.user_b = User.objects.create(
            PhoneNumber="+989123001002",
            first_name="استاد",
            last_name="مشاور ب",
            type_of_user=User.TypeOfUser.ADVISER,
            is_active=True,
            is_verified=True,
        )
        self.adviser_b = Adviser.objects.create(
            user=self.user_b,
            specialization="مشاور کنکور ریاضی",
            can_start_live_session=True,
            is_active=True,
        )

        # دانش‌آموز ۱ (تحت پوشش مشاور الف)
        self.st_user_1 = User.objects.create(
            PhoneNumber="+989123002001",
            first_name="سارا",
            last_name="علوی",
            type_of_user=User.TypeOfUser.STUDENT,
            is_active=True,
            is_verified=True,
        )
        self.student_1 = Student.objects.create(
            user=self.st_user_1,
            adviser=self.adviser_a,
            is_active=True,
        )

        # دانش‌آموز ۲ (تحت پوشش مشاور ب)
        self.st_user_2 = User.objects.create(
            PhoneNumber="+989123002002",
            first_name="نیما",
            last_name="رضوی",
            type_of_user=User.TypeOfUser.STUDENT,
            is_active=True,
            is_verified=True,
        )
        self.student_2 = Student.objects.create(
            user=self.st_user_2,
            adviser=self.adviser_b,
            is_active=True,
        )

        self.counseling_session_a = CounselingSession.objects.create(
            adviser=self.adviser_a,
            student=self.student_1,
            title="جلسه تحلیل کارنامه مهر",
            scheduled_at=datetime2jalali(),
            duration_minutes=45,
            status=CounselingSession.Status.SCHEDULED,
        )

        self.live_a = AdviserLiveSession.objects.create(
            adviser=self.adviser_a,
            counseling_session=self.counseling_session_a,
            title="اتاق آنلاین تحلیل کارنامه سارا",
            server=self.server,
            status=AdviserLiveSession.Status.SCHEDULED,
            scheduled_at=datetime2jalali(),
        )
        self.live_a.students.add(self.student_1)

        self.live_b = AdviserLiveSession.objects.create(
            adviser=self.adviser_b,
            title="اتاق آنلاین مشاور ب",
            server=self.server,
            status=AdviserLiveSession.Status.LIVE,
            scheduled_at=datetime2jalali(),
        )
        self.live_b.students.add(self.student_2)

    def test_session_code_immutability_and_meeting_url_generation(self):
        """تست ۱: بررسی طول ۷۲ کاراکتری کد اختصاصی، غیرقابل تغییر بودن آن و تولید صحیح لینک ورود مشاور و دانش‌آموز"""
        self.assertEqual(len(self.live_a.session_code), 72)
        self.assertFalse(self.live_a.is_available)
        self.assertIsNone(self.live_a.adviser_meeting_url)
        self.assertIsNone(self.live_a.get_student_meeting_url(self.st_user_1))

        # تلاش برای تغییر session_code باید خطای ValidationError بدهد
        old_code = self.live_a.session_code
        self.live_a.session_code = "X" * 72
        with self.assertRaises(ValidationError):
            self.live_a.save()
        self.live_a.session_code = old_code

        # تغییر وضعیت به LIVE و بررسی لینک‌ها
        self.live_a.status = AdviserLiveSession.Status.LIVE
        self.live_a.save(update_fields=["status"])
        self.assertTrue(self.live_a.is_available)

        adviser_url = self.live_a.adviser_meeting_url
        student_url = self.live_a.get_student_meeting_url(self.st_user_1)
        self.assertIn("https://stream.school.ir/teacher.html?", adviser_url)
        self.assertIn(f"room={self.live_a.session_code}", adviser_url)
        self.assertIn("key=SECRET_ADVISER_KEY", adviser_url)
        self.assertIn("https://stream.school.ir/student.html?", student_url)
        self.assertIn(f"room={self.live_a.session_code}", student_url)

    def test_adviser_live_join_view_auto_activates_live_status(self):
        """تست ۲: ورود مشاور به جلسه آنلاین باید خودکار وضعیت را LIVE کند و به آدرس استریم ریدایرکت شود"""
        self.client.force_login(self.user_a)
        self.assertEqual(self.live_a.status, AdviserLiveSession.Status.SCHEDULED)

        resp = self.client.get(reverse("adviser:live-join", kwargs={"pk": self.live_a.pk}))
        self.assertEqual(resp.status_code, 302)
        self.live_a.refresh_from_db()
        self.assertEqual(self.live_a.status, AdviserLiveSession.Status.LIVE)
        self.assertEqual(resp["Location"], self.live_a.adviser_meeting_url)

    def test_adviser_live_session_data_isolation_and_permissions(self):
        """تست ۳: ایزولاسیون داده‌ها بین مشاور الف و مشاور ب + بررسی فلگ دسترسی can_start_live_session"""
        self.client.force_login(self.user_a)

        # مشاور الف نباید به جلسه آنلاین مشاور ب دسترسی داشته باشد
        for route_name, kw in [
            ("adviser:live-join", {"pk": self.live_b.pk}),
            ("adviser:live-update", {"pk": self.live_b.pk}),
            ("adviser:live-report-create", {"live_pk": self.live_b.pk}),
        ]:
            resp = self.client.get(reverse(route_name, kwargs=kw))
            self.assertEqual(resp.status_code, 404)

        # غیرفعال کردن دسترسی شروع جلسه آنلاین برای مشاور الف
        self.adviser_a.can_start_live_session = False
        self.adviser_a.save(update_fields=["can_start_live_session"])
        resp_blocked = self.client.get(reverse("adviser:live-session-list"))
        self.assertEqual(resp_blocked.status_code, 302)
        self.assertRedirects(resp_blocked, reverse("adviser:main"))

    def test_student_live_session_visibility_and_isolation(self):
        """تست ۴: دانش‌آموز فقط جلسات آنلاین مشاور خودش که در آن عضو است را می‌بیند و به جلسه سایرین دسترسی ندارد"""
        self.live_a.status = AdviserLiveSession.Status.LIVE
        self.live_a.save(update_fields=["status"])

        self.client.force_login(self.st_user_1)

        resp_list = self.client.get(reverse("student:counseling-live-list"))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, self.live_a.title)
        self.assertNotContains(resp_list, self.live_b.title)

        resp_detail_ok = self.client.get(
            reverse("student:counseling-live-detail", kwargs={"pk": self.live_a.pk})
        )
        self.assertEqual(resp_detail_ok.status_code, 200)
        self.assertIsNotNone(resp_detail_ok.context["meeting_url"])

        # دانش‌آموز ۱ نباید بتواند جزئیات جلسه مشاور ب را ببیند (404)
        resp_detail_forbidden = self.client.get(
            reverse("student:counseling-live-detail", kwargs={"pk": self.live_b.pk})
        )
        self.assertEqual(resp_detail_forbidden.status_code, 404)

    def test_adviser_live_request_and_report_workflow(self):
        """تست ۵: ثبت درخواست جلسه آنلاین، ثبت گزارش جلسه آنلاین و رندر شدن همه صفحات با کد 200"""
        self.client.force_login(self.user_a)

        # ثبت درخواست جلسه آنلاین
        resp_req = self.client.post(
            reverse("adviser:live-request-create"),
            {
                "title": "درخواست اتاق آنلاین جمع‌بندی آبان",
                "counseling_session": self.counseling_session_a.pk,
                "duration_minutes": 60,
                "description": "نیاز به اتاق آنلاین برای بررسی برنامه آبان",
            },
        )
        self.assertEqual(resp_req.status_code, 302)
        req_obj = AdviserLiveSessionRequest.objects.filter(adviser=self.adviser_a).first()
        self.assertIsNotNone(req_obj)
        self.assertIn(self.student_1, req_obj.students.all())

        # ثبت گزارش برای جلسه آنلاین مشاور الف
        resp_rep = self.client.post(
            reverse("adviser:live-report-create", kwargs={"live_pk": self.live_a.pk}),
            {
                "counseling_session": self.counseling_session_a.pk,
                "duration_minutes": 45,
                "attendees_count": 2,
                "adviser_note": "نقاط قوت و ضعف کارنامه بررسی شد.",
            },
        )
        self.assertEqual(resp_rep.status_code, 302)
        rep_obj = AdviserLiveSessionReport.objects.filter(live_session=self.live_a).first()
        self.assertIsNotNone(rep_obj)
        self.assertEqual(rep_obj.duration_minutes, 45)

        # بررسی رندر شدن تمامی صفحات جدید مشاور (HTTP 200)
        for url in [
            reverse("adviser:live-session-list"),
            reverse("adviser:live-update", kwargs={"pk": self.live_a.pk}),
            reverse("adviser:live-report-update", kwargs={"pk": rep_obj.pk}),
            reverse("adviser:live-request-list"),
            reverse("adviser:live-request-create"),
            reverse("adviser:live-request-detail", kwargs={"pk": req_obj.pk}),
            reverse("adviser:live-request-update", kwargs={"pk": req_obj.pk}),
        ]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, f"Failed rendering {url}")
