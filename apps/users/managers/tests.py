import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.classes.models import Class
from apps.live_classes.models import StreamServers
from apps.schools.models import School
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.managers.excel_utils import build_xlsx_bytes
from apps.users.managers.models import Manager
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher


class SchoolManagerPanelTests(TestCase):
    def setUp(self):
        # مدرسه اول و مدیر اول
        self.manager_user_a = User.objects.create_user(
            PhoneNumber="+989120000001",
            password="Password@123",
            first_name="مدیر",
            last_name="مدرسه الف",
            type_of_user=User.TypeOfUser.MANAGER,
            is_verified=True,
            is_active=True,
        )
        self.manager_a = Manager.objects.create(
            user=self.manager_user_a,
            province="تهران",
            city="تهران",
        )
        self.school_a = School.objects.create(
            user_manager=self.manager_a,
            name="دبیرستان نمونه الف",
            province="تهران",
            city="تهران",
            is_active=True,
        )

        # مدرسه دوم و مدیر دوم (برای تست ایزولاسیون سخت)
        self.manager_user_b = User.objects.create_user(
            PhoneNumber="+989120000002",
            password="Password@123",
            first_name="مدیر",
            last_name="مدرسه ب",
            type_of_user=User.TypeOfUser.MANAGER,
            is_verified=True,
            is_active=True,
        )
        self.manager_b = Manager.objects.create(
            user=self.manager_user_b,
            province="اصفهان",
            city="اصفهان",
        )
        self.school_b = School.objects.create(
            user_manager=self.manager_b,
            name="دبیرستان نمونه ب",
            province="اصفهان",
            city="اصفهان",
            is_active=True,
        )

        # پایه و رشته و درس
        self.grade = GradeCategories.objects.create(name="دوازدهم", is_active=True)
        self.major = MajorCategories.objects.create(name="تجربی", is_active=True)
        self.lesson = LessonCategories.objects.create(name="زیست‌شناسی", is_active=True)

        # کاربران مدرسه الف و ب
        self.student_user_a = User.objects.create_user(
            PhoneNumber="+989121110001",
            password="Password@123",
            first_name="دانش‌آموز",
            last_name="الف",
            type_of_user=User.TypeOfUser.STUDENT,
            is_verified=True,
        )
        self.student_a = Student.objects.create(
            user=self.student_user_a,
            school=self.school_a,
            grade=self.grade,
            major=self.major,
        )

        self.student_user_b = User.objects.create_user(
            PhoneNumber="+989121110002",
            password="Password@123",
            first_name="دانش‌آموز",
            last_name="ب",
            type_of_user=User.TypeOfUser.STUDENT,
            is_verified=True,
        )
        self.student_b = Student.objects.create(
            user=self.student_user_b,
            school=self.school_b,
            grade=self.grade,
            major=self.major,
        )

        self.teacher_user_a = User.objects.create_user(
            PhoneNumber="+989122220001",
            password="Password@123",
            first_name="معلم",
            last_name="الف",
            type_of_user=User.TypeOfUser.TEACHER,
            is_verified=True,
        )
        self.teacher_a = Teacher.objects.create(
            user=self.teacher_user_a,
            school=self.school_a,
        )

        self.adviser_user_a = User.objects.create_user(
            PhoneNumber="+989123330001",
            password="Password@123",
            first_name="مشاور",
            last_name="الف",
            type_of_user=User.TypeOfUser.ADVISER,
            is_verified=True,
        )
        self.adviser_a = Adviser.objects.create(
            user=self.adviser_user_a,
            school=self.school_a,
            max_students_capacity=40,
        )

        # سرورهای استریم (عمومی، اختصاصی مدرسه الف، اختصاصی مدرسه ب)
        self.public_server = StreamServers.objects.create(
            school=None,
            name="سرور عمومی مرکزی",
            base_url="https://live-public.aroedu.ir",
            TEACHER_KEY="pub_key",
            MONITOR_TOKEN="pub_mon",
            is_active=True,
        )
        self.school_a_server = StreamServers.objects.create(
            school=self.school_a,
            name="سرور اختصاصی مدرسه الف",
            base_url="https://live-a.aroedu.ir",
            TEACHER_KEY="a_key",
            MONITOR_TOKEN="a_mon",
            is_active=True,
        )
        self.school_b_server = StreamServers.objects.create(
            school=self.school_b,
            name="سرور اختصاصی مدرسه ب",
            base_url="https://live-b.aroedu.ir",
            TEACHER_KEY="b_key",
            MONITOR_TOKEN="b_mon",
            is_active=True,
        )

    def test_manager_mixin_and_strict_school_isolation(self):
        self.client.force_login(self.manager_user_a)
        resp = self.client.get(reverse("manager:student-list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "دانش‌آموز الف")
        self.assertNotContains(resp, "دانش‌آموز ب")

        # تلاش برای ویرایش دانش‌آموز مدرسه ب باید 404 برگرداند
        resp_other = self.client.get(
            reverse("manager:student-edit", kwargs={"pk": self.student_b.pk})
        )
        self.assertEqual(resp_other.status_code, 404)

    def test_soft_deactivation_only_no_deletion(self):
        self.client.force_login(self.manager_user_a)
        self.assertTrue(self.student_a.is_active)

        resp = self.client.post(
            reverse("manager:student-toggle-active", kwargs={"pk": self.student_a.pk})
        )
        self.assertEqual(resp.status_code, 302)
        self.student_a.refresh_from_db()
        self.student_user_a.refresh_from_db()
        self.assertFalse(self.student_a.is_active)
        self.assertFalse(self.student_user_a.is_active)
        self.assertTrue(Student.objects.filter(pk=self.student_a.pk).exists())

    def test_teacher_and_adviser_permission_control_by_manager(self):
        self.client.force_login(self.manager_user_a)
        resp = self.client.post(
            reverse("manager:teacher-permissions", kwargs={"pk": self.teacher_a.pk}),
            {
                "can_add_exam": False,
                "can_add_practice": True,
                "can_start_live_class": False,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.teacher_a.refresh_from_db()
        self.assertFalse(self.teacher_a.can_add_exam)
        self.assertTrue(self.teacher_a.can_add_practice)
        self.assertFalse(self.teacher_a.can_start_live_class)

        # اگر خود مدیر مجوز تغییر مجوزهای معلم را نداشته باشد، مسدود می‌شود
        self.manager_a.can_change_teacher_permissions = False
        self.manager_a.save()
        resp_denied = self.client.get(
            reverse("manager:teacher-permissions", kwargs={"pk": self.teacher_a.pk})
        )
        self.assertEqual(resp_denied.status_code, 302)

    def test_stream_servers_filtering_school_and_public_only(self):
        self.client.force_login(self.manager_user_a)
        resp = self.client.get(reverse("manager:server-monitor"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "سرور عمومی مرکزی")
        self.assertContains(resp, "سرور اختصاصی مدرسه الف")
        self.assertNotContains(resp, "سرور اختصاصی مدرسه ب")

    def test_bulk_student_excel_import_and_validation(self):
        self.client.force_login(self.manager_user_a)

        # ۱. دانلود قالب اکسل
        tpl_resp = self.client.get(reverse("manager:student-import-template"))
        self.assertEqual(tpl_resp.status_code, 200)
        self.assertTrue(tpl_resp.content.startswith(b"PK"))

        # ۲. ایمپورت موفق با فایل اکسل استاندارد
        headers = [
            "phone_number",
            "first_name",
            "last_name",
            "gender",
            "private_code",
            "grade",
            "major",
        ]
        valid_rows = [
            ["09128880011", "امیر", "رضایی", "M", "1234567890", "دوازدهم", "تجربی"],
            ["09128880022", "مینا", "کریمی", "F", "1234567891", "دوازدهم", "تجربی"],
        ]
        xlsx_bytes = build_xlsx_bytes(headers, valid_rows)
        upload = SimpleUploadedFile(
            "students.xlsx",
            xlsx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        imp_resp = self.client.post(
            reverse("manager:student-import"),
            {"file": upload, "default_adviser": self.adviser_a.pk},
        )
        self.assertEqual(imp_resp.status_code, 302)
        self.assertEqual(
            Student.objects.filter(
                school=self.school_a,
                user__PhoneNumber__in=["+989128880011", "+989128880022"],
            ).count(),
            2,
        )

    def test_advanced_reports_and_client_side_a4_print_report_cards(self):
        self.client.force_login(self.manager_user_a)
        for url_name in (
            "manager:report-exams",
            "manager:report-teachers",
            "manager:report-advisers",
            "manager:report-students",
            "manager:report-cards",
        ):
            r = self.client.get(reverse(url_name))
            self.assertEqual(r.status_code, 200)

            r_print = self.client.get(reverse(url_name) + "?print=1")
            self.assertEqual(r_print.status_code, 200)
            self.assertContains(r_print, "window.print()")

            r_xlsx = self.client.get(reverse(url_name) + "?export=xlsx")
            self.assertEqual(r_xlsx.status_code, 200)
            self.assertTrue(r_xlsx.content.startswith(b"PK"))
