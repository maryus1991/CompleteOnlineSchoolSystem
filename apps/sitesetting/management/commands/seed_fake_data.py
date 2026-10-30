"""
Seed the database with a rich, realistic (Persian) demo dataset.

Sample images and PDFs are taken from the project's own media folder (see
IMAGE_GROUPS / PDF_GROUPS) and copied through the normal Django storage
layer, so every referenced file lands in MEDIA_ROOT automatically.

Usage:
    python manage.py seed_fake_data
"""

from datetime import timedelta, timezone
from io import BytesIO
from pathlib import Path
import random

import jdatetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = ImageDraw = ImageFont = None

from apps.categories.models import (
    BlogCategories,
    GradeCategories,
    LessonCategories,
    MajorCategories,
)
from apps.article.models import Article, ArticleTags
from apps.classes.models import Class
from apps.communication.models import ClassMessage
from apps.content.models import ClassArticle, ClassFile, Section
from apps.exams.models import Exam, ExamStudentDetails
from apps.live_classes.models import (
    AdviserLiveSession,
    AdviserLiveSessionReport,
    AdviserLiveSessionRequest,
    LiveClass,
    LiveClassReport,
    StreamServers,
)
from apps.practice.models import Practice, PracticeStudentDetails
from apps.progress.models import (
    AdviserExamPrescription,
    CounselingSession,
    DailyStudyLog,
    StudyPlan,
    StudyPlanItem,
)
from apps.questions.models import (
    Question,
    QuestionAnswerKey,
    QuestionOption,
    StudentAnswer,
)
from apps.reports.models import ExamReport
from apps.schools.models import School
from apps.sitesetting.models import (
    Contact,
    Counseling,
    FAQ,
    Site,
    TestMonomials,
    TimeLine,
)
from apps.ticket.models import Ticket, TicketChat
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.managers.models import Manager
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher

SEED_MARK = "SEED2026"

# فایل‌های منبع از پوشه media خود پروژه خوانده می‌شوند تا اجرای دستور به
# فایل‌های بیرون از مخزن وابسته نباشد. هر گروه یک الگوی glob نسبت به MEDIA_DIR
# است و فایل‌ها مرتب می‌شوند تا خروجی تکرارپذیر بماند.
MEDIA_DIR = Path(settings.MEDIA_ROOT)

IMAGE_GROUPS = {
    "teacher": "users-profile/**/teacher-*.webp",
    "adviser": "users-profile/**/adviser-*.webp",
    "student": "users-profile/**/student-*.webp",
    "class": "classes/**/class-*.webp",
    "exam": "classes/**/exam-*.webp",
    "article": "articles-images/**/article-*.webp",
    "testimonial": "test-monomials/**/testimonial-*.webp",
    "practice_answer": "practice_answers/**/practice-*-answer-*.jpg",
    "logo": "لوگو/**/site-logo.webp",
    "about": "about-image/**/*.webp",
}

PDF_GROUPS = {
    "class_file": "class-file-*.pdf",
    "article": "article-files/**/article-*.pdf",
    "practice": "questions/**/practice-[0-9].pdf",
    "practice_key": "questions/key/**/practice-answer-key-*.pdf",
    "practice_answer": "practice_answers/**/practice-*-answer-*.pdf",
    "daily_log": "progress/daily_logs/**/daily-log-*.pdf",
    "prescription": "progress/prescriptions/**/prescription-*.pdf",
    "ticket": "tickets/**/ticket-*.pdf",
    "live_recording": "live_classes/recordings/**/live-recording-*.pdf",
    "live_chat": "live_classes/chat_reports/**/live-chat-*.pdf",
    "live_attendance": "live_classes/attendance_reports/**/live-attendance-*.pdf",
}


def J(year, month, day, hour=9, minute=0):
    """Jalali → Gregorian datetime (aware) for Django DateTimeField / DateField."""
    return jdatetime.datetime(
        year, month, day, hour, minute, tzinfo=timezone.utc
    ).togregorian()


def CK(html):
    return f"<p>{html}</p>"


class Command(BaseCommand):
    help = "افزودن داده‌های نمونه‌ی واقع‌گرایانه به دیتابیس و کپی فایل‌ها در media"

    # ------------------------------------------------------------------ utils
    def media_file(self, groups, group, index, name, kind="image"):
        """Load a real media file if present; otherwise build a tiny placeholder.

        Original seed expected files under MEDIA_ROOT matching IMAGE_GROUPS /
        PDF_GROUPS globs. On fresh installs those folders are often empty, so
        we fall back to generated placeholders instead of aborting.
        """
        pattern = groups[group]
        sources = sorted(MEDIA_DIR.glob(pattern))
        if sources:
            return ContentFile(sources[index % len(sources)].read_bytes(), name=name)
        self.stdout.write(
            self.style.WARNING(
                f"منبع media پیدا نشد ({pattern})؛ placeholder ساخته می‌شود: {name}"
            )
        )
        if kind == "pdf" or str(name).lower().endswith(".pdf"):
            return ContentFile(self._placeholder_pdf(name), name=name)
        return ContentFile(self._placeholder_image(name), name=name)

    def image_file(self, group, index, name):
        return self.media_file(IMAGE_GROUPS, group, index, name, kind="image")

    def pdf_file(self, group, index, name):
        return self.media_file(PDF_GROUPS, group, index, name, kind="pdf")

    def _placeholder_image(self, name, size=(640, 480)):
        """Minimal WebP/JPEG/PNG bytes so FileField saves without real assets."""
        label = Path(name).stem[:40]
        ext = Path(name).suffix.lower() or ".webp"
        if Image is None:
            # 1x1 PNG fallback if Pillow is missing
            png = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
                b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            return png
        colors = [
            (41, 98, 255),
            (0, 150, 136),
            (233, 30, 99),
            (255, 152, 0),
            (103, 58, 183),
            (63, 81, 181),
        ]
        color = colors[hash(name) % len(colors)]
        img = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, size[0] - 20, size[1] - 20], outline=(255, 255, 255), width=3)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        text = f"SEED\n{label}"
        # center-ish text
        draw.multiline_text((size[0] // 2 - 40, size[1] // 2 - 20), text, fill=(255, 255, 255), font=font, align="center")
        buf = BytesIO()
        if ext == ".webp":
            img.save(buf, format="WEBP", quality=85)
        elif ext in {".jpg", ".jpeg"}:
            img.save(buf, format="JPEG", quality=85)
        else:
            img.save(buf, format="PNG")
        return buf.getvalue()

    def _placeholder_pdf(self, name):
        """Minimal valid single-page PDF (no external deps)."""
        title = Path(name).stem[:60].replace("(", " ").replace(")", " ")
        # Simple PDF with one page and the filename as text
        content = f"BT /F1 18 Tf 50 750 Td ({title}) Tj ET"
        objects = []
        objects.append("1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
        objects.append("2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
        objects.append(
            "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
        )
        objects.append(
            f"4 0 obj<< /Length {len(content)} >>stream\n{content}\nendstream\nendobj\n"
        )
        objects.append(
            "5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
        )
        body = "".join(objects)
        # Build xref
        header = "%PDF-1.4\n"
        offsets = [0]
        pos = len(header)
        for obj in objects:
            offsets.append(pos)
            pos += len(obj)
        xref_pos = pos
        xref = f"xref\n0 {len(offsets)}\n"
        xref += "0000000000 65535 f \n"
        for off in offsets[1:]:
            xref += f"{off:010d} 00000 n \n"
        trailer = (
            f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        )
        return (header + body + xref + trailer).encode("latin-1")

    def backdate(self, obj, when):
        """created_at / date_joined is auto_now_add; adjust after create.
        `when` must already be a Gregorian datetime (from J()).
        """
        if isinstance(obj, User):
            User.objects.filter(pk=obj.pk).update(date_joined=when)
        else:
            type(obj).objects.filter(pk=obj.pk).update(created_at=when)

    def user(self, phone, first, last, kind, gender, **kwargs):
        user = User.objects.create_user(
            PhoneNumber=phone,
            password="0000",
            first_name=first,
            last_name=last,
            type_of_user=kind,
            gender=gender,
            private_code=SEED_MARK,
            is_verified=True,
            is_active=True,
            **kwargs,
        )
        return user

    # -------------------------------------------------------------------- run
    def handle(self, *args, **options):
        if User.objects.filter(private_code=SEED_MARK).exists():
            raise CommandError("داده‌های نمونه از قبل در دیتابیس وجود دارند.")

        rnd = random.Random(1405)
        self.rnd = rnd

        with transaction.atomic():
            self.seed(options)

        self.stdout.write(self.style.SUCCESS("داده‌های نمونه با موفقیت اضافه شد."))

    # ------------------------------------------------------------------ seeds
    def seed(self, options):
        rnd = self.rnd

        # ------------------------------------------------------- categories
        grade = {}
        for name in ["دهم", "یازدهم", "دوازدهم"]:
            grade[name], _ = GradeCategories.objects.get_or_create(name=name)
        major = {}
        for name in ["تجربی", "ریاضی فیزیک", "انسانی"]:
            major[name], _ = MajorCategories.objects.get_or_create(name=name)
        lesson = {l.name: l for l in LessonCategories.objects.all()}
        for name in ["هندسه", "حسابان", "ادبیات فارسی", "زبان انگلیسی", "عربی", "دین و زندگی", "فیزیک", "شیمی", "ریاضی"]:
            lesson[name], _ = LessonCategories.objects.get_or_create(name=name)
        for name in ["ریاضی", "تجربی", "حسابان", "شیمی", "مشاوره تحصیلی", "انگیزشی"]:
            blog_cat = BlogCategories.objects.filter(name=name).first()
            if not blog_cat:
                BlogCategories.objects.create(name=name)
        blog = {b.name: b for b in BlogCategories.objects.all()}

        # ----------------------------------------------------------- schools
        manager_specs = [
            ("09161130002", "مسعود", "رحیمی", "دزفول", "دبیرستان شهید بهشتی"),
            ("09161130003", "سعید", "بهادری", "اهواز", "دبیرستان دکتر حسابی"),
            ("09161130004", "عبدالله", "کریمی", "اندیمشک", "دبیرستان علامه طباطبایی"),
        ]
        schools = list(School.objects.all()[:1])  # reuse existing school if any
        for i, (phone, first, last, city, school_name) in enumerate(manager_specs, start=1):
            user = self.user(phone, first, last, User.TypeOfUser.MANAGER, User.GenderOfUser.MALE,
                             biography=f"مدیر {school_name}")
            self.backdate(user, J(1405, 5, 12 + i, 9, 15))
            mgr = Manager.objects.create(user=user, province="خوزستان", city=city)
            school = School.objects.create(
                user_manager=mgr,
                name=school_name,
                province="خوزستان",
                city=city,
                is_active=True,
            )
            self.backdate(school, J(1405, 5, 12 + i, 9, 30))
            schools.append(school)
        if not schools:
            raise CommandError("هیچ مدرسه‌ای برای seed وجود ندارد.")
        # school_idx در مشخصات تا ۳ می‌رود؛ اگر فقط ۳ مدرسه ساخته شده، ایندکس‌ها را ایمن می‌کنیم
        def school_at(idx):
            return schools[idx % len(schools)]

        # ---------------------------------------------------------- teachers
        teacher_specs = [
            ("09161110001", "سیدرضا", "موسوی", "M", "ریاضی", 0),
            ("09161110002", "امیرحسین", "کاظمی", "M", "فیزیک", 1),
            ("09161110003", "نگار", "محمدی", "F", "شیمی", 2),
            ("09161110004", "زهرا", "احمدی", "F", "ادبیات فارسی", 0),
            ("09161110005", "مریم", "کاظمی", "F", "زبان انگلیسی", 3),
            ("09161110006", "حجت‌الله", "نادری", "M", "عربی", 3),
        ]
        teachers = []
        for i, (phone, first, last, gender, specialty, school_idx) in enumerate(teacher_specs):
            user = self.user(
                phone, first, last, User.TypeOfUser.TEACHER, gender,
                profile_image=self.image_file("teacher", i, f"teacher-{i + 1}.webp"),
                biography=f"دبیر {specialty} با بیش از {rnd.randint(8, 20)} سال سابقه تدریس",
                publish=True,
            )
            self.backdate(user, J(1405, 5, 20 + i, 10, 0))
            teacher = Teacher.objects.create(
                user=user,
                province="خوزستان",
                city=school_at(school_idx).city,
                school=school_at(school_idx),
                can_add_question=True,
                can_add_qbank=i < 3,
                can_site_article=i == 0,
            )
            self.backdate(teacher, J(1405, 5, 20 + i, 10, 10))
            teachers.append(teacher)

        # ---------------------------------------------------------- advisers
        adviser_specs = [
            ("09161120001", "محمد", "عباسی", "M", "دزفول", 0, "کنکور تجربی و برنامه‌ریزی مطالعاتی"),
            ("09161120002", "فاطمه", "رضایی", "F", "اهواز", 2, "مشاوره تحصیلی و تحلیل آزمون"),
            ("09161120003", "علی", "صادقی", "M", "شوش", 0, "هدایت تحصیلی و انتخاب رشته"),
        ]
        advisers = []
        for i, (phone, first, last, gender, city, school_idx, spec) in enumerate(adviser_specs):
            user = self.user(
                phone, first, last, User.TypeOfUser.ADVISER, gender,
                profile_image=self.image_file("adviser", i, f"adviser-{i + 1}.webp"),
                biography=f"{spec} — {rnd.randint(6, 15)} سال تجربه",
                publish=True,
            )
            self.backdate(user, J(1405, 5, 25 + i, 11, 0))
            adviser = Adviser.objects.create(
                user=user,
                province="خوزستان",
                city=city,
                school=school_at(school_idx),
                specialization=spec,
                max_students_capacity=60,
                can_view_student_reports=True,
                can_manage_sessions=True,
                can_answer_counseling_requests=True,
                can_send_adviser_notes=True,
            )
            self.backdate(adviser, J(1405, 5, 25 + i, 11, 15))
            advisers.append(adviser)

        # ---------------------------------------------------------- students
        student_specs = [
            ("علی", "رضایی", "M", "دوازدهم", "تجربی", "شوش", 0, 0, "پزشکی - رتبه زیر ۵۰۰"),
            ("سارا", "محمدی", "F", "دوازدهم", "تجربی", "دزفول", 1, 1, "داروسازی - رتبه زیر ۸۰۰"),
            ("محمدحسین", "کریمی", "M", "دوازدهم", "ریاضی فیزیک", "شوش", 0, 0, "مهندسی کامپیوتر - دانشگاه تهران"),
            ("زهرا", "حسینی", "F", "دوازدهم", "ریاضی فیزیک", "اهواز", 2, 2, "مهندسی برق - رتبه زیر ۱۰۰۰"),
            ("امیرحسین", "نوری", "M", "یازدهم", "تجربی", "اندیمشک", 3, 1, "پزشکی"),
            ("فاطمه", "احمدی", "F", "یازدهم", "تجربی", "دزفول", 1, 1, "دندان‌پزشکی"),
            ("رضا", "قاسمی", "M", "یازدهم", "ریاضی فیزیک", "شوش", 0, 0, "مهندسی مکانیک"),
            ("مریم", "صادقی", "F", "یازدهم", "انسانی", "اهواز", 2, 2, "حقوق - دانشگاه علامه"),
            ("حسین", "مرادی", "M", "دوازدهم", "انسانی", "شوش", 0, 0, "روان‌شناسی"),
            ("نازنین", "اکبری", "F", "دهم", "تجربی", "دزفول", 1, 1, "پزشکی"),
            ("پارسا", "شریفی", "M", "دهم", "ریاضی فیزیک", "اهواز", 2, 2, "مهندسی عمران"),
            ("یاسمن", "رحیمی", "F", "دهم", "تجربی", "اندیمشک", 3, 1, "بیوتکنولوژی"),
            ("سیدمحمد", "موسوی", "M", "دوازدهم", "تجربی", "شوش", 0, 0, "پزشکی - دانشگاه شهید چمران"),
            ("الهام", "قربانی", "F", "یازدهم", "انسانی", "دزفول", 1, 1, "علوم سیاسی"),
            ("امید", "عالی‌پور", "M", "دوازدهم", "ریاضی فیزیک", "اهواز", 2, 2, "مهندسی هوافضا"),
            ("هانیه", "زارعی", "F", "دهم", "تجربی", "شوش", 0, 0, "پزشکی"),
        ]
        students = []
        for i, (first, last, gender, grade_name, major_name, city, school_idx, adviser_idx, target) in enumerate(student_specs):
            user = self.user(
                f"091712340{i + 1:02d}", first, last, User.TypeOfUser.STUDENT, gender,
                profile_image=self.image_file("student", i, f"student-{i + 1}.webp"),
                biography=f"دانش‌آموز پایه {grade_name} رشته {major_name}",
            )
            self.backdate(user, J(1405, 6, 1 + (i % 20), 8, 30))
            student = Student.objects.create(
                user=user,
                grade=grade[grade_name],
                major=major[major_name],
                province="خوزستان",
                city=city,
                parent_phone_number=f"091633344{i + 1:02d}",
                school=school_at(school_idx),
                adviser=advisers[adviser_idx],
                target_major_rank=target,
                counseling_notes_summary=(
                    f"{first} {last}، دانش‌آموز پایه {grade_name} {major_name} با هدف {target}. "
                    "در جلسات مشاوره، برنامه‌ریزی هفتگی و تحلیل آزمون‌ها به‌صورت منظم انجام می‌شود. "
                    "نیاز به تقویت مهارت تست‌زنی در دروس تخصصی و مدیریت زمان دارد."
                ),
            )
            self.backdate(student, J(1405, 6, 1 + (i % 20), 9, 0))
            students.append(student)

        # ----------------------------------------------------------- classes
        class_specs = [
            ("حسابان ۲ - دوازدهم ریاضی", teachers[0], "دوازدهم", "ریاضی فیزیک", "حسابان", 0, 2400000,
             "مشتق، کاربردهای مشتق و مرور جامع کنکور با حل تست‌های سطح بالا"),
            ("فیزیک دوازدهم - حرکت و دینامیک", teachers[1], "دوازدهم", "تجربی", "فیزیک", 1, 2800000,
             "آموزش مفهومی حرکت‌شناسی، دینامیک و حل مسائل ترکیبی کنکور"),
            ("شیمی یازدهم - شیمی آلی", teachers[2], "یازدهم", "تجربی", "شیمی", 2, 2100000,
             "مرور ساختارها، نام‌گذاری و واکنش‌های ترکیبات آلی همراه با آزمون هفتگی"),
            ("ادبیات فارسی دهم - آرایه‌های ادبی", teachers[3], "دهم", "تجربی", "ادبیات فارسی", 0, 1500000,
             "آرایه‌های ادبی، قرابت معنایی و دستور زبان با تمرین‌های تعاملی"),
            ("زبان انگلیسی یازدهم - گرامر و واژگان", teachers[4], "یازدهم", "انسانی", "زبان انگلیسی", 3, 1300000,
             "تقویت واژگان، گرامر و مهارت خواندن با رویکرد آزمون‌های بین‌المللی"),
            ("هندسه ۲ - یازدهم ریاضی", teachers[0], "یازدهم", "ریاضی فیزیک", "هندسه", 0, 1900000,
             "هندسه تحلیلی، دایره‌ها و مقاطع مخروطی به همراه حل مسائل تشریحی"),
            ("عربی دوازدهم - قواعد و ترجمه", teachers[5], "دوازدهم", "انسانی", "عربی", 3, 1200000,
             "قواعد کاربردی، ترجمه متون و تحلیل سوالات کنکور انسانی"),
        ]
        classes = []
        for i, (name, teacher, grade_name, major_name, lesson_name, school_idx, price, summary) in enumerate(class_specs):
            klass = Class.objects.create(
                school=school_at(school_idx),
                teacher=teacher,
                grade=grade[grade_name],
                major=major[major_name],
                lesson=lesson[lesson_name],
                name=name,
                summery=summary,
                is_public=True,
                is_free=i == 6,
                image=self.image_file("class", i, f"class-{i + 1}.webp"),
                price=price,
                first_tag="پشتیبانی ۲۴/۷",
                second_tag="ضبط جلسات",
                third_tag="آزمون هفتگی",
                text=CK(
                    f"<strong>{name}</strong><br>{summary}. این دوره شامل "
                    f"{rnd.randint(12, 24)} جلسه ویدیویی، جزوه اختصاصی و آزمون‌های منظم است. "
                    "تمام جلسات ضبط شده و تا پایان سال در دسترس دانش‌آموزان قرار دارد."
                ),
            )
            self.backdate(klass, J(1405, 6, 5 + i, 16, 0))
            same_grade = [s for s in students if s.grade_id == grade[grade_name].pk]
            same_major = [s for s in students if s.major_id == major[major_name].pk]
            eligible = [
                s for s in students
                if s.grade_id == grade[grade_name].pk and s.major_id == major[major_name].pk
            ]
            enrolled = []
            for candidate in eligible + same_grade + same_major + students:
                if candidate not in enrolled:
                    enrolled.append(candidate)
                if len(enrolled) >= 5:
                    break
            klass.student.set(enrolled)
            classes.append(klass)

        # ---------------------------------------------------------- sections
        section_specs = [
            ("جلسه ۱ - مفهوم مشتق و قواعد آن", True),
            ("جلسه ۲ - کاربرد مشتق در حل مسئله", True),
            ("جلسه ۳ - تست‌زنی مشتق و جمع‌بندی", True),
            ("جلسه ۱ - حرکت یکنواخت و شتاب‌دار", True),
            ("جلسه ۲ - قوانین نیوتن و دینامیک", True),
            ("جلسه ۳ - حل مسائل ترکیبی حرکت", False),
            ("جلسه ۱ - مقدمه شیمی آلی و آلکان‌ها", True),
            ("جلسه ۲ - آلکن‌ها و آلکین‌ها", True),
            ("جلسه ۳ - مرور و آزمون شیمی آلی", True),
            ("جلسه ۱ - تشبیه و استعاره", True),
            ("جلسه ۲ - کنایه و مجاز", True),
            ("جلسه ۳ - قرابت معنایی", True),
            ("جلسه ۱ - زمان‌های حال و گذشته", True),
            ("جلسه ۲ - واژگان پرتکرار کنکور", True),
            ("جلسه ۳ - درک مطلب", False),
            ("جلسه ۱ - هندسه تحلیلی", True),
            ("جلسه ۲ - دایره و مقاطع مخروطی", True),
            ("جلسه ۳ - حل تمرین هندسه", True),
            ("جلسه ۱ - قواعد باب‌های ثلاثی مزید", True),
            ("جلسه ۲ - ترجمه متون دینی", True),
            ("جلسه ۳ - تحلیل سوالات کنکور", False),
        ]
        sections = []
        for i, (name, publish) in enumerate(section_specs):
            section = Section.objects.create(
                klass=classes[i // 3],
                is_publish=publish,
                name=name,
                sort_number=i % 3 + 1,
            )
            self.backdate(section, J(1405, 6, 8 + i, 17, 0))
            sections.append(section)

        # -------------------------------------------- class articles & files
        article_titles = [
            "جزوه جامع مشتق و کاربردهای آن",
            "نکات طلایی حرکت‌شناسی",
            "جدول واکنش‌های مهم شیمی آلی",
            "آرایه‌های ادبی در یک نگاه",
            "۵۰ واژه پرتکرار زبان انگلیسی",
            "قضیه‌های مهم هندسه ۲",
            "قواعد باب‌های ثلاثی مزید",
        ]
        for i, title in enumerate(article_titles):
            article = ClassArticle.objects.create(
                section=sections[i * 3 + 1],
                name=title,
                content=CK(
                    f"<h3>{title}</h3>"
                    "<p>این محتوا شامل خلاصه درس، نکات کلیدی و مثال‌های حل‌شده است. "
                    "پیشنهاد می‌شود پس از مطالعه، تست‌های انتهای جزوه را حل کنید.</p>"
                    "<ul><li>خلاصه مفهومی درس</li><li>نکات مهم آزمون</li>"
                    "<li>مثال‌های حل‌شده گام به گام</li></ul>"
                ),
            )
            self.backdate(article, J(1405, 6, 10 + i, 18, 0))

            class_file = ClassFile.objects.create(
                section=sections[i * 3 + 2],
                name=f"جزوه و تمرین {title}",
                content=CK("فایل PDF جزوه و تمرین‌های مربوط به این جلسه"),
                file=self.pdf_file("class_file", i, f"class-file-{i + 1}.pdf"),
            )
            self.backdate(class_file, J(1405, 6, 11 + i, 18, 30))

        # -------------------------------------------------------- class chat
        chat_texts = [
            (classes[0], 0, "استاد، در سوال ۱۲ تمرین دوم مشتق، جواب گزینه ۳ درست است؟"),
            (classes[0], None, "بله، فقط دقت کنید دامنه تابع را هم بررسی کنید."),
            (classes[1], 1, "ویدیوی جلسه دوم خیلی عالی بود، ممنون."),
            (classes[1], None, "خواهش می‌کنم؛ تمرین‌های فصل ۲ را تا پنجشنبه ارسال کنید."),
            (classes[2], 4, "جزوه شیمی آلی رو از کجا دانلود کنیم؟"),
            (classes[2], None, "از بخش فایل‌های جلسه ۱، فایل PDF قرار داده شده است."),
            (classes[3], 9, "برای آزمون ادبیات چه فصل‌هایی را بخوانیم؟"),
            (classes[3], None, "فصل‌های ۱ تا ۳ و آرایه‌های تشبیه و استعاره."),
            (classes[5], 2, "سوال ۵ هندسه رو متوجه نشدم."),
            (classes[5], None, "جلسه حل تمرین پنجشنبه ساعت ۱۸ بررسی می‌کنیم."),
            (classes[6], 8, "ترجمه متن دوم را می‌توانید یک بار دیگر توضیح دهید؟"),
            (classes[6], None, "بله، در ابتدای جلسه بعدی مرور می‌کنیم."),
        ]
        for j, (klass, student_idx, text) in enumerate(chat_texts):
            is_teacher = student_idx is None
            ClassMessage.objects.create(
                klass=klass,
                student=None if is_teacher else students[student_idx],
                teacher=klass.teacher if is_teacher else None,
                content=text,
            )

        # ------------------------------------------------------------- exams
        base_date = J(1405, 7, 20, 16, 0)
        exam_specs = [
            {
                "name": "آزمون جامع ریاضی دوازدهم - مرحله ۳",
                "section": "حسابان و هندسه",
                "lesson": "حسابان",
                "grade": "دوازدهم",
                "major": "ریاضی فیزیک",
                "teacher": teachers[0],
                "school": school_at(0),
                "status": Exam.ExamStatus.RESULTS_PUBLISHED,
                "comprehensive": True,
                "start": base_date,
                "image_idx": 0,
                "participants": range(0, 8),
            },
            {
                "name": "آزمون فیزیک دوازدهم - فصل حرکت",
                "section": "حرکت‌شناسی و دینامیک",
                "lesson": "فیزیک",
                "grade": "دوازدهم",
                "major": "تجربی",
                "teacher": teachers[1],
                "school": school_at(1),
                "status": Exam.ExamStatus.RESULTS_PUBLISHED,
                "comprehensive": False,
                "start": J(1405, 7, 26, 17, 0),
                "image_idx": 1,
                "participants": [0, 1, 4, 5, 9, 12, 15],
            },
            {
                "name": "آزمون شیمی یازدهم - شیمی آلی",
                "section": "ترکیبات آلی",
                "lesson": "شیمی",
                "grade": "یازدهم",
                "major": "تجربی",
                "teacher": teachers[2],
                "school": school_at(2),
                "status": Exam.ExamStatus.WAITING_CORRECTION,
                "comprehensive": False,
                "start": J(1405, 8, 2, 16, 0),
                "image_idx": 2,
                "participants": [4, 5, 6, 12],
            },
            {
                "name": "آزمون ادبیات دهم - آرایه‌های ادبی",
                "section": "آرایه‌ها و قرابت",
                "lesson": "ادبیات فارسی",
                "grade": "دهم",
                "major": "تجربی",
                "teacher": teachers[3],
                "school": school_at(0),
                "status": Exam.ExamStatus.WAITING_CORRECTION,
                "comprehensive": False,
                "start": J(1405, 8, 5, 15, 0),
                "image_idx": 3,
                "participants": [9, 11, 15],
            },
        ]

        question_templates = {
            "حسابان": [
                ("مشتق تابع f(x)=x^3-3x^2+2x در نقطه x=1 چند است؟",
                 ["۲", "۱-", "۰", "۳"], 0),
                ("تابع f(x)=x^2-4x+5 در کدام بازه نزولی است؟",
                 ["(-∞,2)", "(2,+∞)", "(-∞,0)", "(0,4)"], 0),
                ("انتگرال ∫(3x^2+2x)dx برابر است با:",
                 ["x^3+x^2+C", "3x^3+2x^2+C", "x^2+x+C", "6x+2+C"], 0),
                ("حد lim(x→0) sin(3x)/x چند است؟",
                 ["۳", "۱", "۰", "∞"], 0),
                ("معادله مماس بر نمودار y=x^2 در نقطه (1,1) کدام است؟",
                 ["y=2x-1", "y=x+1", "y=2x+1", "y=x-1"], 0),
            ],
            "فیزیک": [
                ("جسمی از حال سکون با شتاب ۲ متر بر مجذور ثانیه حرکت می‌کند. سرعت آن پس از ۵ ثانیه چند متر بر ثانیه است؟",
                 ["۱۰", "۵", "۲۰", "۲.۵"], 0),
                ("طبق قانون دوم نیوتن، نیروی خالص وارد بر جسم برابر است با:",
                 ["جرم × شتاب", "جرم ÷ شتاب", "شتاب ÷ جرم", "جرم × سرعت"], 0),
                ("واحد اندازه‌گیری نیرو در SI کدام است؟",
                 ["نیوتن", "ژول", "وات", "پاسکال"], 0),
                ("جسمی با سرعت ثابت ۱۰ متر بر ثانیه در حال حرکت است. شتاب آن چند است؟",
                 ["صفر", "۱۰", "۵", "۲"], 0),
                ("اگر جرم جسمی نصف و نیروی وارد بر آن دو برابر شود، شتاب آن چه تغییری می‌کند؟",
                 ["۴ برابر می‌شود", "نصف می‌شود", "تغییری نمی‌کند", "۲ برابر می‌شود"], 0),
            ],
            "شیمی": [
                ("نام IUPAC ترکیب CH3-CH2-CH3 کدام است؟",
                 ["پروپان", "اتان", "بوتان", "متان"], 0),
                ("کدام ترکیب یک آلکن است؟",
                 ["C2H4", "C2H6", "C2H2", "CH4"], 0),
                ("در واکنش سوختن کامل متان، کدام محصولات تشکیل می‌شوند؟",
                 ["CO2 و H2O", "CO و H2", "C و H2O", "CO2 و H2"], 0),
                ("فرمول عمومی آلکان‌ها کدام است؟",
                 ["CnH2n+2", "CnH2n", "CnH2n-2", "CnHn"], 0),
                ("کدام گروه عاملی در الکل‌ها وجود دارد؟",
                 ["-OH", "-COOH", "-CHO", "-NH2"], 0),
            ],
            "ادبیات فارسی": [
                ("در عبارت «دلش دریای غم بود»، کدام آرایه به کار رفته است؟",
                 ["تشبیه", "کنایه", "جناس", "تضاد"], 0),
                ("«سرو چمان» در بیت «سرو چمان من چرا میل چمن نمی‌کند» استعاره از چیست؟",
                 ["معشوق", "درخت سرو", "باغبان", "بهار"], 0),
                ("کدام واژه با واژه «گل» جناس دارد؟",
                 ["گل (خاک)", "بلبل", "بهار", "باغ"], 0),
                ("در «شب تار» کدام آرایه دیده می‌شود؟",
                 ["تشخیص", "استعاره", "اضافه تشبیهی", "کنایه"], 0),
                ("معنای کنایی «دست و پا گم کردن» چیست؟",
                 ["سردرگم شدن", "ورزش کردن", "فرار کردن", "خسته شدن"], 0),
            ],
        }

        exams = []
        for ei, spec in enumerate(exam_specs):
            start = spec["start"]
            stop = start + timedelta(hours=2)
            last_enter = start + timedelta(hours=1, minutes=45)
            exam = Exam.objects.create(
                status=spec["status"],
                name=spec["name"],
                section=spec["section"],
                type_of_quiz="آزمون آنلاین",
                price=0 if ei == 3 else 350000,
                time_minutes=120,
                start_at=start,
                stop_at=stop,
                last_enter=last_enter,
                corrected_at=start + timedelta(days=2),
                max_score=100,
                score=2 if ei == 0 else 1.5,
                capacity=100,
                filled_capacity=len(list(spec["participants"])),
                have_negative_score=True,
                grade=grade[spec["grade"]],
                major=major[spec["major"]],
                lesson=lesson[spec["lesson"]],
                school=spec["school"],
                province="خوزستان",
                city=spec["school"].city,
                description=CK(
                    f"<p>{spec['name']} با طراحی سوالات استاندارد و تحلیل کارنامه در کارنامه‌ی آزمون.</p>"
                ),
                is_public=True,
                is_free=ei == 3,
                image=self.image_file("exam", spec["image_idx"], f"exam-{ei + 1}.webp"),
                summery=f"آزمون {spec['section']} - {spec['grade']} {spec['major']}",
                comprehensive_exam=spec["comprehensive"],
            )
            self.backdate(exam, start - timedelta(days=12))
            exam.teacher.add(spec["teacher"])
            participant_list = [students[p] for p in spec["participants"]]
            exam.selected_student.set(participant_list)
            exam.entered_student.set(participant_list)
            exams.append(exam)

            questions = []
            for qi, (qname, options, correct_idx) in enumerate(question_templates[spec["lesson"]]):
                q = Question.objects.create(
                    teacher=spec["teacher"],
                    name=qname,
                    description=CK(qname),
                    score=20,
                    type_of_question=Question.TypeOfQuestions.MULTIPLE_CHOICE,
                    is_for_qbank=True,
                    exam=exam,
                    grade=grade[spec["grade"]],
                    major=major[spec["major"]],
                    lesson=lesson[spec["lesson"]],
                    sort_number=qi + 1,
                )
                opts = [
                    QuestionOption.objects.create(
                        question=q, name=text, is_correct=(idx == correct_idx)
                    )
                    for idx, text in enumerate(options)
                ]
                QuestionAnswerKey.objects.create(
                    question=q,
                    type_of_answer=QuestionAnswerKey.TypeOfAnswer.TEXT_BASED,
                    description=CK(f"پاسخ صحیح: {options[correct_idx]}"),
                )
                questions.append((q, opts, correct_idx))
            self.backdate(exam, start - timedelta(days=12))

            # answers and reports
            reports = []
            for pi, student in enumerate(participant_list):
                answered = 0
                correct_count = 0
                wrong_count = 0
                skipped_count = 0
                total_score = 0.0
                for qi, (q, opts, correct_idx) in enumerate(questions):
                    # deterministic mix of correct / wrong / skipped
                    roll = rnd.random()
                    if roll < 0.08:
                        StudentAnswer.objects.create(
                            type_of_answer=StudentAnswer.TypeOfAnswer.SKIPPED,
                            question=q,
                            student=student,
                            exam=exam,
                            corrected=StudentAnswer.TypeOfCorrect.not_corrected,
                            score=0,
                        )
                        skipped_count += 1
                        continue
                    if roll < 0.72:
                        chosen = opts[correct_idx]
                        quality = StudentAnswer.TypeOfCorrect.excellent
                        score = 20
                        correct_count += 1
                    else:
                        chosen = rnd.choice([o for i, o in enumerate(opts) if i != correct_idx])
                        quality = rnd.choice(
                            [StudentAnswer.TypeOfCorrect.wrong, StudentAnswer.TypeOfCorrect.weak]
                        )
                        score = 0
                        wrong_count += 1
                    StudentAnswer.objects.create(
                        type_of_answer=StudentAnswer.TypeOfAnswer.OPTION,
                        selected_option=chosen,
                        question=q,
                        student=student,
                        exam=exam,
                        corrected=quality,
                        corrected_at=stop,
                        corrected_by=spec["teacher"],
                        score=score,
                        sanatorium_message=CK("پاسخ بررسی شد."),
                    )
                    answered += 1
                    total_score += score

                ExamStudentDetails.objects.create(
                    exam=exam,
                    student=student,
                    student_finished_at=stop - timedelta(minutes=rnd.randint(2, 30)),
                    out_of_page=rnd.randint(0, 2),
                )
                report = ExamReport.objects.create(
                    exam=exam,
                    student=student,
                    status=ExamReport.ReportStatus.PUBLISHED,
                    total_questions=len(questions),
                    correct_count=correct_count,
                    wrong_count=wrong_count,
                    unanswered_count=0,
                    skipped_count=skipped_count,
                    uncorrected_count=0,
                    score=total_score,
                    max_score=100,
                    percentage=min(100, max(0, total_score)),
                    answered_percentage=round((answered / len(questions)) * 100, 2),
                    calculated_at=stop + timedelta(days=1),
                    published_at=stop + timedelta(days=2),
                )
                self.backdate(report, stop + timedelta(days=2))
                reports.append(report)

            reports.sort(key=lambda r: r.percentage, reverse=True)
            percentages = [r.percentage for r in reports]
            avg = sum(percentages) / len(percentages)
            variance = sum((p - avg) ** 2 for p in percentages) / len(percentages)
            for rank, report in enumerate(reports, start=1):
                report.rank = rank
                report.teraze = round(6000 + (report.percentage - avg) * 15, 1)
                report.save(update_fields=["rank", "teraze"])
            Exam.objects.filter(pk=exam.pk).update(
                average_percentage=round(avg, 2),
                std_percentage=round(variance ** 0.5, 2),
                average_score=round(avg, 2),
                std_score=round(variance ** 0.5, 2),
                participants_count=len(participant_list),
                stats_calculated_at=stop + timedelta(days=2),
            )

        # ---------------------------------------------------------- practices
        practice_specs = [
            (sections[2], "تمرین مشتق - سری اول", teachers[0], 0, [0, 2, 6, 14]),
            (sections[5], "تمرین حرکت‌شناسی - مسائل ترکیبی", teachers[1], 1, [0, 1, 4, 12]),
            (sections[8], "تمرین شیمی آلی - نام‌گذاری", teachers[2], 2, [4, 5, 15]),
            (sections[11], "تمرین آرایه‌های ادبی", teachers[3], 3, [9, 11, 15]),
        ]
        for pi, (section, name, teacher, idx, student_indexes) in enumerate(practice_specs):
            practice = Practice.objects.create(
                section=section,
                name=name,
                description=CK(
                    f"<p>{name}: سوالات را با دقت بخوانید و پاسخ‌ها را در مهلت مقرر ارسال کنید. "
                    "برای سوالات تشریحی، فایل پاسخ خود را بارگذاری نمایید.</p>"
                ),
                type_of_practice=Practice.TypeOfQuestions.LONG_ANSWER,
                start_at=J(1405, 7, 10 + pi, 18, 0),
                deadline=J(1405, 7, 17 + pi, 23, 0),
                creator=teacher.user,
            )
            self.backdate(practice, J(1405, 7, 10 + pi, 17, 30))
            chosen_students = [students[s] for s in student_indexes]
            practice.selected_students.set(chosen_students)

            q1 = Question.objects.create(
                teacher=teacher,
                name=f"سوال ۱ - {name}",
                description=CK("پاسخ خود را با ذکر مراحل حل بنویسید."),
                score=10,
                type_of_question=Question.TypeOfQuestions.LONG_ANSWER,
                practice=practice,
                grade=section.klass.grade,
                major=section.klass.major,
                lesson=section.klass.lesson,
            )
            QuestionAnswerKey.objects.create(
                question=q1,
                type_of_answer=QuestionAnswerKey.TypeOfAnswer.TEXT_BASED,
                description=CK("پاسخ کامل با ذکر مراحل و نتیجه نهایی."),
            )
            q2 = Question.objects.create(
                teacher=teacher,
                name=f"سوال ۲ - {name}",
                description=CK("فایل حل خود را بارگذاری کنید."),
                score=10,
                type_of_question=Question.TypeOfQuestions.PDF_BASED,
                practice=practice,
                pdf_file=self.pdf_file("practice", pi, f"practice-{pi + 1}.pdf"),
                grade=section.klass.grade,
                major=section.klass.major,
                lesson=section.klass.lesson,
            )
            QuestionAnswerKey.objects.create(
                question=q2,
                type_of_answer=QuestionAnswerKey.TypeOfAnswer.PDF_BASED,
                pdf_file=self.pdf_file("practice_key", pi, f"practice-answer-key-{pi + 1}.pdf"),
            )

            for si, student in enumerate(chosen_students):
                status = (
                    PracticeStudentDetails.Status.CORRECTED if si % 2 == 0
                    else PracticeStudentDetails.Status.SUBMITTED
                )
                d1 = PracticeStudentDetails.objects.create(
                    practice=practice,
                    question=q1,
                    student=student,
                    status=status,
                    started_at=J(1405, 7, 12 + pi, 19, 0),
                    student_finished_at=J(1405, 7, 14 + pi, 20, 0),
                    submitted_at=J(1405, 7, 14 + pi, 20, 0),
                    corrected_at=J(1405, 7, 16 + pi, 10, 0) if status == PracticeStudentDetails.Status.CORRECTED else None,
                    answer_text=(
                        "مراحل حل را با استفاده از قواعد مشتق انجام دادم و نتیجه نهایی "
                        f"{rnd.randint(2, 12)} به دست آمد."
                    ),
                    answer_image=(
                        self.image_file("practice_answer", pi + si, f"practice-{pi + 1}-answer-{si + 1}.jpg")
                        if si % 3 == 0 else None
                    ),
                    score=float(rnd.choice([6, 7, 8, 9])) if status == PracticeStudentDetails.Status.CORRECTED else None,
                    teacher_feedback="پاسخ شما بررسی شد؛ به نوشتن واحدها و مراحل دقت کنید."
                    if status == PracticeStudentDetails.Status.CORRECTED else "",
                )
                self.backdate(d1, J(1405, 7, 14 + pi, 20, 0))
                d2 = PracticeStudentDetails.objects.create(
                    practice=practice,
                    question=q2,
                    student=student,
                    status=status,
                    started_at=J(1405, 7, 13 + pi, 18, 0),
                    student_finished_at=J(1405, 7, 15 + pi, 21, 0),
                    submitted_at=J(1405, 7, 15 + pi, 21, 0),
                    corrected_at=J(1405, 7, 16 + pi, 11, 0) if status == PracticeStudentDetails.Status.CORRECTED else None,
                    answer_pdf=(
                        self.pdf_file("practice_answer", pi + si, f"practice-{pi + 1}-answer-{si + 1}.pdf")
                        if si % 2 == 0 else None
                    ),
                    score=float(rnd.choice([7, 8, 9, 10])) if status == PracticeStudentDetails.Status.CORRECTED else None,
                    teacher_feedback="فایل پاسخ دریافت و تصحیح شد."
                    if status == PracticeStudentDetails.Status.CORRECTED else "",
                )
                self.backdate(d2, J(1405, 7, 15 + pi, 21, 0))

        # ------------------------------------------------------- study plans
        plan_specs = [
            (0, 0, "برنامه هفتگی آمادگی کنکور - مهر", StudyPlan.Status.ACTIVE,
             J(1405, 7, 1), J(1405, 7, 30)),
            (1, 1, "برنامه جبران و تقویت فیزیک", StudyPlan.Status.ACTIVE,
             J(1405, 7, 5), J(1405, 8, 5)),
            (2, 0, "برنامه مرور و تست‌زنی حسابان", StudyPlan.Status.COMPLETED,
             J(1405, 6, 1), J(1405, 6, 30)),
            (4, 1, "برنامه مطالعاتی شیمی یازدهم", StudyPlan.Status.ACTIVE,
             J(1405, 7, 20), J(1405, 8, 20)),
            (8, 0, "برنامه مطالعاتی ادبیات و عربی", StudyPlan.Status.DRAFT,
             J(1405, 8, 10), J(1405, 9, 10)),
        ]
        plan_topics = [
            ("مشتق و قواعد آن", "reading", 90, 0),
            ("تست‌زنی مشتق", "testing", 60, 40),
            ("مرور کاربرد مشتق", "review", 45, 0),
            ("حرکت‌شناسی", "reading", 100, 0),
            ("حل مسائل دینامیک", "class_practice", 75, 0),
            ("آزمون آزمایشی", "exam_analysis", 120, 0),
            ("شیمی آلی: آلکان‌ها", "reading", 80, 0),
            ("تست شیمی آلی", "testing", 50, 30),
            ("آرایه‌های ادبی", "reading", 45, 0),
            ("قرابت معنایی", "testing", 40, 20),
        ]
        plans = []
        for pi, (student_idx, adviser_idx, title, status, start, end) in enumerate(plan_specs):
            plan = StudyPlan.objects.create(
                student=students[student_idx],
                adviser=advisers[adviser_idx],
                title=title,
                start_date=start,
                end_date=end,
                adviser_description=CK(
                    "این برنامه با توجه به سطح فعلی و هدف دانش‌آموز طراحی شده است. "
                    "لطفا هر شب گزارش کار روزانه را ثبت کنید و در پایان هفته عملکرد خود را با مشاور مرور کنید."
                ),
                status=status,
            )
            self.backdate(plan, start)
            for ii, (topic, study_type, duration, tests) in enumerate(plan_topics):
                day = ii % 7
                item = StudyPlanItem.objects.create(
                    study_plan=plan,
                    day_of_week=day,
                    lesson=lesson[
                        ["حسابان", "فیزیک", "شیمی", "ادبیات فارسی"][ii % 4]
                    ],
                    topic=topic,
                    study_type=study_type,
                    target_duration_minutes=duration,
                    target_test_count=tests,
                    priority=rnd.choice(
                        [StudyPlanItem.Priority.MEDIUM, StudyPlanItem.Priority.HIGH, StudyPlanItem.Priority.LOW]
                    ),
                    is_completed_by_student=(ii < 5 and status != StudyPlan.Status.DRAFT),
                    completed_at=(start + timedelta(days=day)) if (ii < 5 and status != StudyPlan.Status.DRAFT) else None,
                    adviser_tip="زمان‌بندی را رعایت کن و بعد از هر مطالعه، خلاصه‌نویسی کوتاه انجام بده.",
                    sort_number=ii + 1,
                )
                self.backdate(item, start)
            plans.append(plan)

        # ------------------------------------------------------ daily logs
        log_specs = [
            (0, 0, 0, 120, 40, 30, 5, "خواندن فصل مشتق و حل تمرین‌های تشریحی", "عالی بود، ادامه بده."),
            (0, 0, 1, 90, 30, 22, 4, "تست‌زنی مشتق و بررسی غلط‌ها", "غلط‌ها را به دفتر اشتباهات منتقل کن."),
            (0, 0, 2, 150, 50, 30, 5, "مرور کامل فصل حرکت و دینامیک", "روند خوبی داری."),
            (1, 1, 0, 100, 30, 25, 3, "حل مسائل حرکت‌شناسی", "تمرکز روی سوالات ترکیبی بیشتر شود."),
            (1, 1, 1, 80, 20, 18, 4, "مرور فرمول‌های دینامیک", "خوب است."),
            (2, 0, 0, 140, 60, 40, 4, "حسابان: کاربرد مشتق", "نیاز به مرور بیشتر در بخش اکسترمم‌ها."),
            (2, 0, 1, 110, 45, 35, 5, "تست‌زنی جامع حسابان", "پیشرفت خوبی داشتی."),
            (4, 1, 0, 95, 25, 20, 3, "شیمی آلی: آلکن‌ها", "واکنش‌ها را دوباره مرور کن."),
            (4, 1, 1, 70, 15, 12, 4, "مرور جدول واکنش‌ها", "بهتر شد."),
            (9, 0, 0, 60, 20, 15, 3, "آرایه‌های ادبی: تشبیه", "تمرین بیشتری لازم است."),
            (9, 0, 1, 55, 18, 14, 4, "قرابت معنایی", "خوب پیش می‌روی."),
            (12, 1, 0, 130, 55, 38, 5, "آزمون آزمایشی و تحلیل آن", "تحلیل آزمون را کامل ثبت کن."),
        ]
        for li, (student_idx, adviser_idx, item_idx, duration, total, correct, focus, note, feedback) in enumerate(log_specs):
            log_date = J(1405, 7, 20, 21, 30) + timedelta(days=li)
            student_plans = [p for p in plans if p.student_id == students[student_idx].pk]
            active_plan = student_plans[0] if student_plans else plans[0]
            plan_item = active_plan.items.all()[item_idx] if active_plan.items.exists() else None
            dlog = DailyStudyLog.objects.create(
                student=students[student_idx],
                study_plan_item=plan_item,
                lesson=plan_item.lesson if plan_item else next(iter(lesson.values())),
                log_date=log_date,
                actual_duration_minutes=duration,
                tests_total=total,
                tests_correct=correct,
                tests_wrong=max(0, total - correct),
                focus_quality=focus,
                student_note=note,
                attachment=(
                    self.pdf_file("daily_log", li, f"daily-log-{li + 1}.pdf") if li % 3 == 0 else None
                ),
                review_status=DailyStudyLog.ReviewStatus.APPROVED if li % 3 != 2 else DailyStudyLog.ReviewStatus.PENDING,
                adviser_feedback=feedback if li % 3 != 2 else "",
                reviewed_at=log_date + timedelta(hours=2) if li % 3 != 2 else None,
            )
            self.backdate(dlog, log_date)

        # ------------------------------------------- prescription on reports
        prescription_reports = ExamReport.objects.filter(exam=exams[0])[:3]
        analyses = [
            ("تسلط خوب در مبحث مشتق و کاربردهای آن", "افت در تست‌های هندسه تحلیلی و مدیریت زمان",
             "هفته آینده ۲ آزمون ۳۰ سوالی مشتق در زمان ۴۵ دقیقه حل شود"),
            ("پاسخ‌گویی دقیق در سوالات مفهومی", "اشتباه محاسباتی در سوالات ترکیبی",
             "دفتر اشتباهات تشکیل شود و هر شب ۱۰ تست مرور گردد"),
            ("روند رو به رشد در درصد حسابان", "بی‌دقتی در سوالات سطح متوسط",
             "تمرین‌های زمان‌دار و بازبینی پاسخ‌ها پس از هر آزمون"),
        ]
        for ri, report in enumerate(prescription_reports):
            strengths, weaknesses, action = analyses[ri % len(analyses)]
            prescription = AdviserExamPrescription.objects.create(
                exam_report=report,
                adviser=advisers[0],
                student=report.student,
                strengths_analysis=CK(strengths),
                weaknesses_analysis=CK(weaknesses),
                action_plan_for_next_exam=CK(action),
                voice_or_file_attachment=self.pdf_file("prescription", ri, f"prescription-{ri + 1}.pdf"),
                is_seen_by_student=ri % 2 == 0,
                student_reflection=(
                    "برنامه را مطالعه کردم و از هفته آینده اجرا می‌کنم."
                    if ri % 2 == 0 else None
                ),
            )
            self.backdate(prescription, J(1405, 7, 27 + ri, 12, 0))

        # ------------------------------------------------- counseling session
        session_specs = [
            (0, 0, "بررسی برنامه هفتگی و هدف‌گذاری", CounselingSession.SessionType.ONLINE_MEET,
             CounselingSession.Status.SCHEDULED, J(1405, 8, 9, 17, 0)),
            (1, 1, "تحلیل آزمون فیزیک و رفع اشکال", CounselingSession.SessionType.PHONE,
             CounselingSession.Status.COMPLETED, J(1405, 7, 28, 19, 0)),
            (2, 0, "انتخاب رشته و اولویت‌بندی دانشگاه", CounselingSession.SessionType.IN_PERSON,
             CounselingSession.Status.COMPLETED, J(1405, 7, 15, 11, 0)),
            (4, 1, "مشاوره انگیزشی و مدیریت استرس", CounselingSession.SessionType.ONLINE_MEET,
             CounselingSession.Status.CANCELLED, J(1405, 8, 1, 16, 0)),
            (5, 1, "برنامه‌ریزی شیمی آلی", CounselingSession.SessionType.ONLINE_MEET,
             CounselingSession.Status.REQUESTED_BY_STUDENT, J(1405, 8, 12, 18, 0)),
            (8, 0, "مرور برنامه ادبیات و عربی", CounselingSession.SessionType.PHONE,
             CounselingSession.Status.SCHEDULED, J(1405, 8, 15, 20, 0)),
        ]
        for si, (student_idx, adviser_idx, title, s_type, status, when) in enumerate(session_specs):
            session = CounselingSession.objects.create(
                adviser=advisers[adviser_idx],
                student=students[student_idx],
                title=title,
                session_type=s_type,
                scheduled_at=when,
                duration_minutes=45 if s_type != CounselingSession.SessionType.PHONE else 30,
                meeting_link="https://meet.example.com/counseling-room" if s_type == CounselingSession.SessionType.ONLINE_MEET else "",
                status=status,
                student_request_note="برای بهبود برنامه مطالعاتی نیاز به راهنمایی دارم.",
                session_summary=CK(
                    "در این جلسه وضعیت مطالعه، نقاط قوت و ضعف بررسی شد و تصمیم‌های زیر گرفته شد: "
                    "تنظیم ساعت مطالعه شبانه، افزایش تست‌زنی و ثبت گزارش کار روزانه."
                ) if status == CounselingSession.Status.COMPLETED else None,
                private_adviser_note="دانش‌آموز نیاز به پیگیری هفتگی دارد.",
            )
            self.backdate(session, when - timedelta(days=3))

        # ------------------------------------------------------------- tickets
        ticket_specs = [
            (0, 0, "مشکل در دانلود جزوه جلسه دوم", Ticket.TicketPriority.mid,
             Ticket.TicketStatus.fixed,
             "سلام، هنگام دانلود فایل PDF جزوه جلسه دوم خطای ۴۰۴ دریافت می‌کنم. لطفا بررسی کنید."),
            (1, 1, "درخواست تغییر زمان آزمون", Ticket.TicketPriority.high,
             Ticket.TicketStatus.awating_admin,
             "با سلام، آزمون فیزیک با کلاس مدرسه هم‌زمان شده است. امکان تغییر زمان وجود دارد؟"),
            (2, 2, "عدم نمایش کارنامه آزمون", Ticket.TicketPriority.huge,
             Ticket.TicketStatus.awating_user,
             "سلام، بعد از آزمون جامع، کارنامه من در پنل نمایش داده نمی‌شود."),
            (3, 4, "درخواست دسترسی به ویدیوی ضبط‌شده", Ticket.TicketPriority.low,
             Ticket.TicketStatus.fixed,
             "لطفا دسترسی ویدیوی جلسه سوم را برای من فعال کنید."),
        ]
        admin_user = User.objects.filter(is_superuser=True).first()
        for ti, (student_idx, _, name, priority, status, description) in enumerate(ticket_specs):
            ticket = Ticket.objects.create(
                name=name,
                user=students[student_idx].user,
                description=description,
                file=self.pdf_file("ticket", ti, f"ticket-{ti + 1}.pdf") if ti % 2 == 0 else None,
                priority=priority,
                status=status,
            )
            self.backdate(ticket, J(1405, 7, 18 + ti, 10, 0))
            TicketChat.objects.create(
                ticket=ticket,
                user_message=description,
                is_read_by_admin=True,
            )
            if admin_user:
                TicketChat.objects.create(
                    ticket=ticket,
                    admin=admin_user,
                    admin_message=CK(
                        "سلام، درخواست شما بررسی شد. لطفا در صورت نیاز اطلاعات بیشتری ارسال کنید."
                    ),
                    is_read_by_user=True,
                )
            if status == Ticket.TicketStatus.fixed:
                TicketChat.objects.create(
                    ticket=ticket,
                    user_message="ممنون از پیگیری شما، مشکل حل شد.",
                    is_read_by_admin=True,
                )

        # --------------------------------------------------- live class rooms
        server = StreamServers.objects.first()
        if server:
            live_specs = [
                (classes[0], LiveClass.Status.COMPLETED, sections[0]),
                (classes[1], LiveClass.Status.COMPLETED, sections[4]),
                (classes[2], LiveClass.Status.SCHEDULED, sections[6]),
                (classes[5], LiveClass.Status.LIVE, sections[16]),
            ]
            for li, (klass, status, section) in enumerate(live_specs):
                live = LiveClass.objects.create(
                    klass=klass,
                    server=server,
                    status=status,
                )
                self.backdate(live, J(1405, 7, 22 + li, 17, 0))
                if status == LiveClass.Status.COMPLETED:
                    report = LiveClassReport.objects.create(
                        live_class=live,
                        section=section,
                        started_at=J(1405, 7, 22 + li, 17, 0),
                        ended_at=J(1405, 7, 22 + li, 18, 30),
                        duration_minutes=90,
                        attendees_count=rnd.randint(12, 32),
                        teacher_note="جلسه با حضور فعال دانش‌آموزان برگزار شد و تمرین‌های فصل مرور گردید.",
                        admin_note="کیفیت صدا و تصویر مناسب بود.",
                        recording_file=self.pdf_file("live_recording", li, f"live-recording-{li + 1}.pdf"),
                        chat_report=self.pdf_file("live_chat", li, f"live-chat-{li + 1}.pdf"),
                        attendance_report=self.pdf_file("live_attendance", li, f"live-attendance-{li + 1}.pdf"),
                    )
                    self.backdate(report, J(1405, 7, 22 + li, 18, 45))

            # اتاق‌های جلسه آنلاین مشاوره (برای مشاوران و دانش‌آموزان تحت پوشش)
            for ai, adv in enumerate(advisers):
                adv_students = list(Student.objects.filter(adviser=adv, user__is_active=True)[:3])
                adv_session = CounselingSession.objects.filter(adviser=adv).first()
                live_adv = AdviserLiveSession.objects.create(
                    adviser=adv,
                    counseling_session=adv_session,
                    title=f"جلسه آنلاین مشاوره و بررسی برنامه ({adv.user.get_full_name()})",
                    server=server,
                    status=AdviserLiveSession.Status.LIVE if ai == 0 else AdviserLiveSession.Status.COMPLETED,
                    scheduled_at=J(1405, 7, 25 + ai, 16, 0),
                )
                if adv_students:
                    live_adv.students.set(adv_students)
                self.backdate(live_adv, J(1405, 7, 25 + ai, 16, 0))

                if live_adv.status == AdviserLiveSession.Status.COMPLETED:
                    adv_rep = AdviserLiveSessionReport.objects.create(
                        live_session=live_adv,
                        counseling_session=adv_session,
                        started_at=J(1405, 7, 25 + ai, 16, 0),
                        ended_at=J(1405, 7, 25 + ai, 16, 45),
                        duration_minutes=45,
                        attendees_count=len(adv_students) + 1,
                        adviser_note="برنامه مطالعاتی هفتگی و بودجه‌بندی آزمون بعدی با دانش‌آموزان هماهنگ شد.",
                        admin_note="جلسه مشاوره بدون مشکل فنی برگزار گردید.",
                        recording_file=self.pdf_file("live_recording", ai, f"adviser-live-rec-{ai + 1}.pdf"),
                        chat_report=self.pdf_file("live_chat", ai, f"adviser-live-chat-{ai + 1}.pdf"),
                        attendance_report=self.pdf_file("live_attendance", ai, f"adviser-live-att-{ai + 1}.pdf"),
                    )
                    self.backdate(adv_rep, J(1405, 7, 25 + ai, 17, 0))

                req_adv = AdviserLiveSessionRequest.objects.create(
                    adviser=adv,
                    counseling_session=adv_session,
                    title=f"درخواست جلسه آنلاین تحلیل آزمون ({adv.user.get_full_name()})",
                    description="درخواست اختصاص اتاق آنلاین جهت جلسه تحلیل کارنامه و هدف‌گذاری آزمون بعدی.",
                    preferred_at=J(1405, 8, 2 + ai, 17, 30),
                    duration_minutes=45,
                    status=AdviserLiveSessionRequest.Status.APPROVED if ai == 0 else AdviserLiveSessionRequest.Status.PENDING,
                    admin_note="اتاق آنلاین روی سرور اصلی فعال شد." if ai == 0 else "",
                )
                if adv_students:
                    req_adv.students.set(adv_students)
                self.backdate(req_adv, J(1405, 7, 24 + ai, 12, 0))

        # ------------------------------------------------------------ articles
        article_specs = [
            ("هفت راهکار علمی برای افزایش تمرکز در مطالعه", "ریاضی", 7,
             "تمرکز، مهم‌ترین ابزار دانش‌آموز است. در این مقاله تکنیک‌های عملی برای افزایش تمرکز را بررسی می‌کنیم.",
             ["تمرکز", "مطالعه", "مدیریت زمان"]),
            ("چگونه آزمون‌های آزمایشی را تحلیل کنیم؟", "تجربی", 9,
             "تحلیل آزمون، ارزشمندتر از خود آزمون است. روش تحلیل سوال به سوال را بیاموزید.",
             ["آزمون", "تحلیل آزمون", "کنکور"]),
            ("برنامه‌ریزی مطالعاتی که واقعا جواب می‌دهد", "مشاوره تحصیلی", 6,
             "یک برنامه خوب باید انعطاف‌پذیر باشد. اصول طراحی برنامه هفتگی موثر را مرور می‌کنیم.",
             ["برنامه‌ریزی", "مشاوره", "عادات مطالعه"]),
            ("شیمی آلی را چگونه مفهومی بخوانیم؟", "شیمی", 8,
             "حفظ کردن واکنش‌ها کافی نیست. با درک ساختار و مکانیزم‌ها، شیمی آلی را آسان بیاموزید.",
             ["شیمی", "شیمی آلی", "کنکور"]),
            ("انگیزه در مسیر کنکور: از هیجان تا استمرار", "انگیزشی", 5,
             "انگیزه کوتاه‌مدت کافی نیست؛ عادت‌سازی و هدف‌های کوچک، کلید موفقیت است.",
             ["انگیزه", "استمرار", "موفقیت"]),
        ]
        for ai, (title, cat_name, minutes, summary, tags) in enumerate(article_specs):
            article = Article.objects.create(
                user=teachers[ai % len(teachers)].user,
                category=blog.get(cat_name) or blog["ریاضی"],
                reading_time=minutes,
                name=title,
                summery=summary,
                text=CK(
                    f"<h2>{title}</h2><p>{summary}</p>"
                    "<p>در این بخش به بررسی جزئیات، مثال‌های کاربردی و تمرین‌های پیشنهادی می‌پردازیم. "
                    "پیشنهاد می‌شود مطالب را با دفتر یادداشت خود مقایسه کرده و به‌صورت عملی اجرا کنید.</p>"
                    "<h3>جمع‌بندی</h3><p>با تمرین مستمر و بازخورد گرفتن از مشاور، می‌توانید روند رو به رشدی را تجربه کنید.</p>"
                ),
                image=self.image_file("article", ai, f"article-{ai + 1}.webp"),
                file=self.pdf_file("article", ai, f"article-{ai + 1}.pdf"),
                name_for_file=f"فایل تکمیلی {title}",
                publish=True,
            )
            self.backdate(article, J(1405, 6, 20 + ai, 12, 0))
            for tag in tags:
                ArticleTags.objects.create(
                    post=article,
                    name=tag,
                    url=f"/posts/?tag={tag}",
                )

        # --------------------------------------------------------- site texts
        testimonial_specs = [
            ("سارا محمدی", "دانش‌آموز پایه دوازدهم تجربی", "با برنامه‌ریزی مشاور، درصد زیست من از ۳۰ به ۶۵ رسید."),
            ("علی رضایی", "رتبه ۴۸۰ کنکور تجربی", "پشتیبانی و تحلیل آزمون‌ها بهترین بخش این مجموعه بود."),
            ("مریم صادقی", "دانش‌آموز پایه یازدهم انسانی", "کلاس‌های آنلاین با کیفیت و جزوه‌های کامل، مطالعه را آسان کرد."),
        ]
        for i, (name, behave, text) in enumerate(testimonial_specs):
            t = TestMonomials.objects.create(
                name=name,
                behave=behave,
                text=text,
                image=self.image_file("testimonial", i, f"testimonial-{i + 1}.webp"),
            )
            self.backdate(t, J(1405, 6, 25 + i, 14, 0))

        timeline_specs = [
            ("مشاوره اولیه", "تعیین سطح و هدف‌گذاری تحصیلی"),
            ("طراحی برنامه", "برنامه‌ریزی شخصی‌سازی‌شده هفتگی"),
            ("پشتیبانی مستمر", "تحلیل آزمون و رفع اشکال"),
            ("ارزیابی نهایی", "مرور عملکرد و تعیین مسیر آزمون بعدی"),
        ]
        for i, (name, description) in enumerate(timeline_specs):
            tm = TimeLine.objects.create(name=name, description=description)
            self.backdate(tm, J(1405, 6, 10 + i, 15, 0))

        contact_specs = [
            ("مهدی یاوری", "09165550101", "سلام، برای ثبت‌نام کلاس حسابان راهنمایی می‌خواستم.", True),
            ("سمیرا نجفی", "09165550102", "آیا کلاس‌های ضبط‌شده هم دسترسی دارند؟", False),
            ("حمید قنبری", "09165550103", "برای مشاوره انتخاب رشته وقت آزاد دارید؟", False),
        ]
        for i, (name, phone, message, read) in enumerate(contact_specs):
            c = Contact.objects.create(
                full_name=name, phone_number=phone, message=message, read=read
            )
            self.backdate(c, J(1405, 7, 5 + i, 11, 0))

        counseling_request_specs = [
            ("پریسا مرادی", "09165550201", "برای پایه دوازدهم تجربی مشاور می‌خواهم.", Counseling.Status.NEW, None, ""),
            ("میلاد کوهی", "09165550202", "امکان مشاوره تلفنی برای برنامه ریاضی هست؟", Counseling.Status.IN_PROGRESS,
             advisers[0], "در حال هماهنگی برای جلسه اولیه."),
            ("نرگس ابراهیمی", "09165550203", "برای انتخاب رشته انسانی راهنمایی لازم دارم.", Counseling.Status.DONE,
             advisers[1], "جلسه مشاوره انجام شد و رشته‌های پیشنهادی ارسال گردید."),
        ]
        for i, (name, phone, message, status, who, note) in enumerate(counseling_request_specs):
            c = Counseling.objects.create(
                full_name=name,
                phone_number=phone,
                message=message,
                status=status,
                assigned_adviser=who,
                adviser_follow_up_note=note,
                read=status != Counseling.Status.NEW,
            )
            self.backdate(c, J(1405, 7, 10 + i, 13, 0))

        faq_specs = [
            ("آیا جلسات ضبط می‌شوند؟", "بله، تمام جلسات کلاس‌های آنلاین ضبط شده و تا پایان سال تحصیلی در پنل دانش‌آموز قابل مشاهده است."),
            ("هزینه کلاس‌ها چگونه پرداخت می‌شود؟", "پرداخت به‌صورت آنلاین از طریق درگاه امن سایت انجام می‌شود و امکان پرداخت اقساطی نیز وجود دارد."),
            ("آیا امکان جبران جلسه غایب وجود دارد؟", "بله، دانش‌آموزان می‌توانند ویدیوی ضبط‌شده جلسه را مشاهده کنند و در جلسه رفع اشکال هفتگی شرکت نمایند."),
            ("مشاوره تحصیلی چگونه انجام می‌شود؟", "ابتدا فرم مشاوره را تکمیل می‌کنید، سپس مشاور با شما تماس گرفته و جلسه اولیه را هماهنگ می‌کند."),
        ]
        for i, (question, answer) in enumerate(faq_specs):
            f = FAQ.objects.create(question=question, answer=CK(answer))
            self.backdate(f, J(1405, 6, 28 + i, 10, 0))

        # ------------------------------------------------- site branding files
        site = Site.objects.first()
        if site:
            if not site.logo:
                site.logo.save("site-logo.webp", self.image_file("logo", 0, "site-logo.webp"), save=True)
            if not site.about_img:
                site.about_img.save("about-us.webp", self.image_file("about", 0, "about-us.webp"), save=True)
            site.short_description = "بنیاد آموزشی فراسو؛ همراه دانش‌آموزان در مسیر موفقیت تحصیلی"
            site.save(update_fields=["short_description"])

        self.stdout.write(
            "  کاربران: %d | مدارس: %d | کلاس‌ها: %d | آزمون‌ها: %d | مقالات: %d"
            % (
                User.objects.filter(private_code=SEED_MARK).count(),
                School.objects.count(),
                Class.objects.count(),
                Exam.objects.count(),
                Article.objects.count(),
            )
        )