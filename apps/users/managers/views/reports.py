from collections import defaultdict
from django.db.models import Avg, Count, Max, Min, Prefetch, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import TemplateView

from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.exams.models import Exam
from apps.progress.models import DailyStudyLog
from apps.questions.models import Question, StudentAnswer
from apps.reports.models import ExamReport
from apps.users.managers.excel_utils import build_xlsx_bytes
from apps.users.managers.mixins import ManagerMixin


class BaseManagerReportView(ManagerMixin, TemplateView):
    """
    کلاس پایه گزارش‌گیری پیشرفته پنل مدیر مدرسه:
    - ذخیره موقت فیلترها در Session
    - محاسبه زمان تولید گزارش و تعداد نتایج
    - خروجی اکسل (.xlsx)
    - حالت پرینت و تولید PDF سمت کاربر (Client-Side Print / Save as PDF در قالب استاندارد A4)
    """

    permission_field = "can_view_reports"
    print_template_name = None
    session_filter_key = "manager_report_filters"

    def get_template_names(self):
        if self.request.GET.get("print") == "1" and self.print_template_name:
            return [self.print_template_name]
        return [self.template_name]

    def get_active_filters(self) -> dict:
        req = self.request
        if req.GET.get("reset_filters") == "1":
            req.session.pop(self.session_filter_key, None)
            return {}

        filter_keys = (
            "class_id",
            "grade_id",
            "major_id",
            "lesson_id",
            "teacher_id",
            "adviser_id",
            "student_id",
            "exam_id",
            "pass_threshold",
        )
        stored = dict(req.session.get(self.session_filter_key, {}))
        has_query_params = any(k in req.GET for k in filter_keys)
        if has_query_params:
            current = {}
            for k in filter_keys:
                val = (req.GET.get(k) or "").strip()
                if val:
                    current[k] = val
            req.session[self.session_filter_key] = current
            return current
        return stored

    def get_pass_threshold(self, filters: dict) -> float:
        raw = filters.get("pass_threshold", "50")
        try:
            val = float(raw)
            return max(0.0, min(100.0, val))
        except (ValueError, TypeError):
            return 50.0

    def get_common_filter_context(self, filters: dict) -> dict:
        return {
            "filters": filters,
            "pass_threshold": self.get_pass_threshold(filters),
            "generated_at": timezone.localtime(timezone.now()),
            "is_print_mode": self.request.GET.get("print") == "1",
            "grades": GradeCategories.objects.filter(is_active=True),
            "majors": MajorCategories.objects.filter(is_active=True),
            "lessons": LessonCategories.objects.filter(is_active=True),
            "classes_list": self.get_school_classes_queryset().filter(is_active=True),
            "teachers_list": self.get_school_teachers_queryset().filter(is_active=True),
            "advisers_list": self.get_school_advisers_queryset().filter(is_active=True),
            "students_list": self.get_school_students_queryset().filter(is_active=True),
            "exams_list": self.get_school_exams_queryset().filter(is_active=True),
        }

    @staticmethod
    def export_xlsx_response(
        filename: str, headers: list[str], rows: list[list], sheet_name: str = "Report"
    ) -> HttpResponse:
        content = build_xlsx_bytes(headers, rows, sheet_name=sheet_name)
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# ============================================================
# ۱. گزارش جامع آزمون‌ها (تحلیل سوال به سوال + مقایسه کلاس و پایه)
# ============================================================
class ManagerExamReportView(BaseManagerReportView):
    template_name = "manager/reports/exams_report.html"
    print_template_name = "manager/reports/print_exams_report.html"

    def get(self, request, *args, **kwargs):
        filters = self.get_active_filters()
        data = self.build_report_data(filters)
        if request.GET.get("export") == "xlsx":
            headers = [
                "ردیف",
                "عنوان آزمون",
                "درس",
                "پایه",
                "وضعیت",
                "تعداد شرکت‌کنندگان",
                "میانگین نمره",
                "بیشترین نمره",
                "کمترین نمره",
                "میانگین درصد",
                "درصد قبولی",
            ]
            rows = []
            for idx, item in enumerate(data["exam_rows"], start=1):
                rows.append(
                    [
                        idx,
                        item["exam"].name,
                        item["exam"].lesson.name if item["exam"].lesson else "-",
                        item["exam"].grade.name if item["exam"].grade else "-",
                        item["exam"].status or "-",
                        item["participants"],
                        item["avg_score"],
                        item["max_score"],
                        item["min_score"],
                        item["avg_pct"],
                        f"{item['pass_rate']}%",
                    ]
                )
            return self.export_xlsx_response(
                "school_exams_comprehensive_report.xlsx",
                headers,
                rows,
                sheet_name="ExamsReport",
            )
        ctx = self.get_context_data(**kwargs)
        ctx.update(self.get_common_filter_context(filters))
        ctx.update(data)
        return self.render_to_response(ctx)

    def build_report_data(self, filters: dict) -> dict:
        school = self.get_school()
        pass_threshold = self.get_pass_threshold(filters)
        exams_qs = self.get_school_exams_queryset()

        grade_id = filters.get("grade_id", "")
        major_id = filters.get("major_id", "")
        lesson_id = filters.get("lesson_id", "")
        teacher_id = filters.get("teacher_id", "")
        exam_id = filters.get("exam_id", "")
        class_id = filters.get("class_id", "")

        if grade_id.isdigit():
            exams_qs = exams_qs.filter(grade_id=int(grade_id))
        if major_id.isdigit():
            exams_qs = exams_qs.filter(major_id=int(major_id))
        if lesson_id.isdigit():
            exams_qs = exams_qs.filter(lesson_id=int(lesson_id))
        if teacher_id.isdigit():
            exams_qs = exams_qs.filter(teacher__id=int(teacher_id))
        if exam_id.isdigit():
            exams_qs = exams_qs.filter(id=int(exam_id))

        report_filter = Q(reports__student__school=school, reports__is_active=True)
        if class_id.isdigit():
            report_filter &= Q(reports__student__classes__id=int(class_id))

        annotated_exams = exams_qs.annotate(
            participants_num=Count("reports", filter=report_filter, distinct=True),
            avg_score_val=Avg("reports__score", filter=report_filter),
            max_score_val=Max("reports__score", filter=report_filter),
            min_score_val=Min("reports__score", filter=report_filter),
            avg_pct_val=Avg("reports__percentage", filter=report_filter),
            pass_count_val=Count(
                "reports",
                filter=report_filter & Q(reports__percentage__gte=pass_threshold),
                distinct=True,
            ),
        ).order_by("-pk")

        exam_rows = []
        for ex in annotated_exams:
            part = ex.participants_num or 0
            p_cnt = ex.pass_count_val or 0
            exam_rows.append(
                {
                    "exam": ex,
                    "participants": part,
                    "avg_score": round(ex.avg_score_val or 0, 2),
                    "max_score": round(ex.max_score_val or 0, 2),
                    "min_score": round(ex.min_score_val or 0, 2),
                    "avg_pct": round(ex.avg_pct_val or 0, 1),
                    "pass_count": p_cnt,
                    "pass_rate": round((p_cnt / part) * 100, 1) if part else 0.0,
                }
            )

        # تحلیل سوال به سوال (برای آزمون انتخاب‌شده یا آزمون‌های فیلترشده)
        target_exam_ids = [r["exam"].id for r in exam_rows[:10]]
        questions_qs = (
            Question.objects.filter(exam_id__in=target_exam_ids, is_active=True)
            .select_related("exam", "lesson")
            .annotate(
                total_ans=Count(
                    "student_answers",
                    filter=Q(student_answers__student__school=school),
                ),
                correct_ans=Count(
                    "student_answers",
                    filter=Q(
                        student_answers__student__school=school,
                        student_answers__corrected=StudentAnswer.TypeOfCorrect.excellent,
                    )
                    | Q(
                        student_answers__student__school=school,
                        student_answers__selected_option__is_correct=True,
                    ),
                ),
                wrong_ans=Count(
                    "student_answers",
                    filter=Q(
                        student_answers__student__school=school,
                        student_answers__corrected=StudentAnswer.TypeOfCorrect.wrong,
                    ),
                ),
            )
            .order_by("exam_id", "pk")[:60]
        )
        question_analysis = []
        for idx, q_obj in enumerate(questions_qs, start=1):
            tot = q_obj.total_ans or 0
            cor = q_obj.correct_ans or 0
            question_analysis.append(
                {
                    "index": idx,
                    "question": q_obj,
                    "total_answers": tot,
                    "correct_answers": cor,
                    "wrong_answers": q_obj.wrong_ans or 0,
                    "correct_pct": round((cor / tot) * 100, 1) if tot else 0.0,
                }
            )

        # مقایسه بین پایه‌ها و کلاس‌های مدرسه
        grade_comparison = list(
            ExamReport.objects.filter(
                student__school=school,
                exam_id__in=[r["exam"].id for r in exam_rows],
                is_active=True,
            )
            .values("student__grade__name")
            .annotate(
                reports_count=Count("id"),
                avg_pct=Avg("percentage"),
                avg_score=Avg("score"),
            )
            .order_by("-avg_pct")
        )
        class_comparison = list(
            self.get_school_classes_queryset()
            .filter(is_active=True)
            .annotate(
                reports_count=Count(
                    "student__exam_reports",
                    filter=Q(
                        student__exam_reports__exam_id__in=[
                            r["exam"].id for r in exam_rows
                        ]
                    ),
                    distinct=True,
                ),
                avg_pct=Avg(
                    "student__exam_reports__percentage",
                    filter=Q(
                        student__exam_reports__exam_id__in=[
                            r["exam"].id for r in exam_rows
                        ]
                    ),
                ),
            )
            .order_by("-avg_pct")
        )

        return {
            "exam_rows": exam_rows,
            "results_count": len(exam_rows),
            "question_analysis": question_analysis,
            "grade_comparison": grade_comparison,
            "class_comparison": class_comparison,
        }


# ============================================================
# ۲. گزارش عملکرد معلمان مدرسه
# ============================================================
class ManagerTeacherReportView(BaseManagerReportView):
    template_name = "manager/reports/teachers_report.html"
    print_template_name = "manager/reports/print_teachers_report.html"

    def get(self, request, *args, **kwargs):
        filters = self.get_active_filters()
        data = self.build_report_data(filters)
        if request.GET.get("export") == "xlsx":
            headers = [
                "ردیف",
                "نام معلم",
                "شماره تماس",
                "تعداد کلاس‌ها",
                "تعداد جلسات",
                "محتوای آموزشی (مقاله/فایل)",
                "تعداد آزمون‌ها",
                "تعداد تمرین‌ها",
                "تعداد سوالات طراحی‌شده",
                "میانگین درصد دانش‌آموزان",
                "تیکت‌های ارجاعی",
            ]
            rows = []
            for idx, item in enumerate(data["teacher_rows"], start=1):
                rows.append(
                    [
                        idx,
                        str(item["teacher"]),
                        str(item["teacher"].user.PhoneNumber),
                        item["classes_num"],
                        item["sections_num"],
                        item["content_num"],
                        item["exams_num"],
                        item["practices_num"],
                        item["questions_num"],
                        f"{item['avg_student_pct']}%",
                        item["assigned_tickets_num"],
                    ]
                )
            return self.export_xlsx_response(
                "school_teachers_performance_report.xlsx",
                headers,
                rows,
                sheet_name="TeachersReport",
            )
        ctx = self.get_context_data(**kwargs)
        ctx.update(self.get_common_filter_context(filters))
        ctx.update(data)
        return self.render_to_response(ctx)

    def build_report_data(self, filters: dict) -> dict:
        school = self.get_school()
        teachers_qs = self.get_school_teachers_queryset()
        teacher_id = filters.get("teacher_id", "")
        if teacher_id.isdigit():
            teachers_qs = teachers_qs.filter(id=int(teacher_id))

        annotated = teachers_qs.annotate(
            classes_num=Count("classes", distinct=True),
            sections_num=Count("classes__sections", distinct=True),
            articles_num=Count("classes__sections__article", distinct=True),
            files_num=Count("classes__sections__file", distinct=True),
            practices_num=Count("classes__sections__practices", distinct=True),
            exams_num=Count("exam", distinct=True),
            questions_num=Count("questions", distinct=True),
            corrected_num=Count("corrected_answers", distinct=True),
            assigned_tickets_num=Count("assigned_tickets", distinct=True),
            avg_student_score_val=Avg(
                "exam__reports__score",
                filter=Q(exam__reports__student__school=school),
            ),
            avg_student_pct_val=Avg(
                "exam__reports__percentage",
                filter=Q(exam__reports__student__school=school),
            ),
        ).order_by("-classes_num", "-exams_num", "-pk")

        teacher_rows = []
        for t in annotated:
            articles_c = t.articles_num or 0
            files_c = t.files_num or 0
            teacher_rows.append(
                {
                    "teacher": t,
                    "classes_num": t.classes_num or 0,
                    "sections_num": t.sections_num or 0,
                    "articles_num": articles_c,
                    "files_num": files_c,
                    "content_num": articles_c + files_c,
                    "practices_num": t.practices_num or 0,
                    "exams_num": t.exams_num or 0,
                    "questions_num": t.questions_num or 0,
                    "corrected_num": t.corrected_num or 0,
                    "assigned_tickets_num": t.assigned_tickets_num or 0,
                    "avg_student_score": round(t.avg_student_score_val or 0, 2),
                    "avg_student_pct": round(t.avg_student_pct_val or 0, 1),
                }
            )

        return {
            "teacher_rows": teacher_rows,
            "results_count": len(teacher_rows),
        }


# ============================================================
# ۳. گزارش عملکرد مشاوران مدرسه
# ============================================================
class ManagerAdviserReportView(BaseManagerReportView):
    template_name = "manager/reports/advisers_report.html"
    print_template_name = "manager/reports/print_advisers_report.html"

    def get(self, request, *args, **kwargs):
        filters = self.get_active_filters()
        data = self.build_report_data(filters)
        if request.GET.get("export") == "xlsx":
            headers = [
                "ردیف",
                "نام مشاور",
                "تخصص",
                "دانش‌آموزان تحت پوشش",
                "ظرفیت کل",
                "جلسات مشاوره (کل / برگزارشده)",
                "جلسات آنلاین",
                "برنامه‌های مطالعاتی",
                "نسخه‌های کارنامه",
                "میانگین درصد آزمون دانش‌آموزان",
                "تیکت‌های ارجاعی",
            ]
            rows = []
            for idx, item in enumerate(data["adviser_rows"], start=1):
                rows.append(
                    [
                        idx,
                        str(item["adviser"]),
                        item["adviser"].specialization or "-",
                        item["covered_students_num"],
                        item["adviser"].max_students_capacity,
                        f"{item['sessions_total_num']} / {item['sessions_completed_num']}",
                        item["live_sessions_num"],
                        item["study_plans_num"],
                        item["prescriptions_num"],
                        f"{item['avg_students_pct']}%",
                        item["assigned_tickets_num"],
                    ]
                )
            return self.export_xlsx_response(
                "school_advisers_performance_report.xlsx",
                headers,
                rows,
                sheet_name="AdvisersReport",
            )
        ctx = self.get_context_data(**kwargs)
        ctx.update(self.get_common_filter_context(filters))
        ctx.update(data)
        return self.render_to_response(ctx)

    def build_report_data(self, filters: dict) -> dict:
        advisers_qs = self.get_school_advisers_queryset()
        adviser_id = filters.get("adviser_id", "")
        if adviser_id.isdigit():
            advisers_qs = advisers_qs.filter(id=int(adviser_id))

        annotated = advisers_qs.annotate(
            covered_students_num=Count(
                "students", filter=Q(students__is_active=True), distinct=True
            ),
            sessions_total_num=Count("sessions", distinct=True),
            sessions_completed_num=Count(
                "sessions",
                filter=Q(sessions__status="completed"),
                distinct=True,
            ),
            live_sessions_num=Count("live_sessions", distinct=True),
            study_plans_num=Count("created_study_plans", distinct=True),
            prescriptions_num=Count("exam_prescriptions", distinct=True),
            assigned_tickets_num=Count("assigned_tickets", distinct=True),
            logs_reviewed_num=Count(
                "students__daily_logs",
                filter=Q(students__daily_logs__review_status="approved"),
                distinct=True,
            ),
            avg_students_pct_val=Avg("students__exam_reports__percentage"),
        ).order_by("-covered_students_num", "-pk")

        adviser_rows = []
        for adv in annotated:
            covered = adv.covered_students_num or 0
            cap = adv.max_students_capacity or 50
            adviser_rows.append(
                {
                    "adviser": adv,
                    "covered_students_num": covered,
                    "remaining_capacity": max(0, cap - covered),
                    "capacity_pct": min(100, round((covered / cap) * 100)) if cap else 0,
                    "sessions_total_num": adv.sessions_total_num or 0,
                    "sessions_completed_num": adv.sessions_completed_num or 0,
                    "live_sessions_num": adv.live_sessions_num or 0,
                    "study_plans_num": adv.study_plans_num or 0,
                    "prescriptions_num": adv.prescriptions_num or 0,
                    "logs_reviewed_num": adv.logs_reviewed_num or 0,
                    "assigned_tickets_num": adv.assigned_tickets_num or 0,
                    "avg_students_pct": round(adv.avg_students_pct_val or 0, 1),
                }
            )

        return {
            "adviser_rows": adviser_rows,
            "results_count": len(adviser_rows),
        }


# ============================================================
# ۴. گزارش عملکرد و پیشرفت دانش‌آموزان مدرسه
# ============================================================
class ManagerStudentReportView(BaseManagerReportView):
    template_name = "manager/reports/students_report.html"
    print_template_name = "manager/reports/print_students_report.html"

    def get(self, request, *args, **kwargs):
        filters = self.get_active_filters()
        data = self.build_report_data(filters)
        if request.GET.get("export") == "xlsx":
            headers = [
                "ردیف",
                "نام دانش‌آموز",
                "شماره موبایل",
                "پایه",
                "رشته",
                "مشاور",
                "کلاس‌های ثبت‌نامی",
                "آزمون‌های شرکت‌کرده",
                "میانگین نمره آزمون",
                "میانگین درصد آزمون",
                "بهترین رتبه",
                "تمرین‌های ارسالی",
                "مجموع دقیقه مطالعه",
            ]
            rows = []
            for idx, item in enumerate(data["student_rows"], start=1):
                st = item["student"]
                rows.append(
                    [
                        idx,
                        str(st),
                        str(st.user.PhoneNumber),
                        st.grade.name if st.grade else "-",
                        st.major.name if st.major else "-",
                        str(st.adviser) if st.adviser else "-",
                        item["classes_num"],
                        item["exams_num"],
                        item["avg_exam_score"],
                        f"{item['avg_exam_pct']}%",
                        item["best_rank"] or "-",
                        item["practices_num"],
                        item["study_minutes"],
                    ]
                )
            return self.export_xlsx_response(
                "school_students_performance_report.xlsx",
                headers,
                rows,
                sheet_name="StudentsReport",
            )
        ctx = self.get_context_data(**kwargs)
        ctx.update(self.get_common_filter_context(filters))
        ctx.update(data)
        return self.render_to_response(ctx)

    def build_report_data(self, filters: dict) -> dict:
        school = self.get_school()
        students_qs = self.get_school_students_queryset()

        class_id = filters.get("class_id", "")
        grade_id = filters.get("grade_id", "")
        major_id = filters.get("major_id", "")
        adviser_id = filters.get("adviser_id", "")
        student_id = filters.get("student_id", "")

        if class_id.isdigit():
            students_qs = students_qs.filter(classes__id=int(class_id))
        if grade_id.isdigit():
            students_qs = students_qs.filter(grade_id=int(grade_id))
        if major_id.isdigit():
            students_qs = students_qs.filter(major_id=int(major_id))
        if adviser_id.isdigit():
            students_qs = students_qs.filter(adviser_id=int(adviser_id))
        if student_id.isdigit():
            students_qs = students_qs.filter(id=int(student_id))

        school_avg_pct = (
            ExamReport.objects.filter(student__school=school, is_active=True).aggregate(
                avg=Avg("percentage")
            )["avg"]
            or 0.0
        )

        annotated = (
            students_qs.annotate(
                classes_num=Count("classes", distinct=True),
                exams_num=Count("exam_reports", distinct=True),
                avg_exam_score_val=Avg("exam_reports__score"),
                avg_exam_pct_val=Avg("exam_reports__percentage"),
                best_rank_val=Min("exam_reports__rank"),
                practices_num=Count("practice_details", distinct=True),
                avg_practice_score_val=Avg("practice_details__score"),
                study_minutes_val=Sum("daily_logs__actual_duration_minutes"),
            )
            .distinct()
            .order_by("-avg_exam_pct_val", "-exams_num", "-pk")
        )

        student_rows = []
        for idx, st in enumerate(annotated, start=1):
            avg_pct = round(st.avg_exam_pct_val or 0, 1)
            student_rows.append(
                {
                    "rank_in_list": idx,
                    "student": st,
                    "classes_num": st.classes_num or 0,
                    "exams_num": st.exams_num or 0,
                    "avg_exam_score": round(st.avg_exam_score_val or 0, 2),
                    "avg_exam_pct": avg_pct,
                    "diff_from_school_avg": round(avg_pct - school_avg_pct, 1),
                    "best_rank": st.best_rank_val,
                    "practices_num": st.practices_num or 0,
                    "avg_practice_score": round(st.avg_practice_score_val or 0, 2),
                    "study_minutes": st.study_minutes_val or 0,
                }
            )

        return {
            "student_rows": student_rows,
            "school_avg_pct": round(school_avg_pct, 1),
            "results_count": len(student_rows),
        }


# ============================================================
# ۵. کارنامه رسمی دانش‌آموز (تکی و دسته‌جمعی کل کلاس/پایه - قابل پرینت A4)
# ============================================================
class ManagerStudentReportCardView(BaseManagerReportView):
    """
    صدور کارنامه رسمی و کامل دانش‌آموز (تک دانش‌آموز یا چاپ دسته‌جمعی کل یک کلاس / پایه)
    با قالب استاندارد A4 و تولید و پرینت PDF سمت کاربر (Client-Side Print / PDF).
    """

    template_name = "manager/reports/report_cards.html"
    print_template_name = "manager/reports/report_card_print.html"

    def get(self, request, *args, **kwargs):
        filters = self.get_active_filters()
        data = self.build_report_cards(filters)
        if request.GET.get("export") == "xlsx":
            headers = [
                "رتبه کل",
                "نام دانش‌آموز",
                "کد ملی / اختصاصی",
                "پایه",
                "رشته",
                "کلاس‌ها",
                "تعداد آزمون",
                "معدل نمره",
                "میانگین درصد کل",
                "وضعیت نهایی",
            ]
            rows = []
            for card in data["report_cards"]:
                st = card["student"]
                rows.append(
                    [
                        card["overall_rank"],
                        str(st),
                        st.user.private_code or "-",
                        st.grade.name if st.grade else "-",
                        st.major.name if st.major else "-",
                        " | ".join(c.name for c in card["enrolled_classes"]) or "-",
                        card["total_exams"],
                        card["overall_avg_score"],
                        f"{card['overall_avg_pct']}%",
                        card["pass_status_label"],
                    ]
                )
            return self.export_xlsx_response(
                "school_official_report_cards.xlsx",
                headers,
                rows,
                sheet_name="ReportCards",
            )
        ctx = self.get_context_data(**kwargs)
        ctx.update(self.get_common_filter_context(filters))
        ctx.update(data)
        return self.render_to_response(ctx)

    def build_report_cards(self, filters: dict) -> dict:
        school = self.get_school()
        pass_threshold = self.get_pass_threshold(filters)
        students_qs = self.get_school_students_queryset().filter(is_active=True)

        student_id = filters.get("student_id", "")
        class_id = filters.get("class_id", "")
        grade_id = filters.get("grade_id", "")
        major_id = filters.get("major_id", "")

        if student_id.isdigit():
            students_qs = students_qs.filter(id=int(student_id))
        if class_id.isdigit():
            students_qs = students_qs.filter(classes__id=int(class_id))
        if grade_id.isdigit():
            students_qs = students_qs.filter(grade_id=int(grade_id))
        if major_id.isdigit():
            students_qs = students_qs.filter(major_id=int(major_id))

        reports_prefetch = Prefetch(
            "exam_reports",
            queryset=ExamReport.objects.filter(is_active=True)
            .select_related("exam", "exam__lesson", "exam__grade")
            .prefetch_related("adviser_prescription")
            .order_by("exam__lesson__name", "-pk"),
            to_attr="prefetched_exam_reports",
        )
        students_list = list(
            students_qs.prefetch_related("classes", reports_prefetch).distinct()[:60]
        )

        # میانگین هر آزمون در مدرسه برای ستون مقایسه با میانگین کلاس/مدرسه
        exam_avg_map = dict(
            ExamReport.objects.filter(student__school=school, is_active=True)
            .values_list("exam_id")
            .annotate(avg_pct=Avg("percentage"))
        )

        raw_cards = []
        for st in students_list:
            exam_reports = getattr(st, "prefetched_exam_reports", [])
            lesson_groups = defaultdict(list)
            total_score_sum = 0.0
            total_pct_sum = 0.0
            adviser_comments = []

            exam_items = []
            for rep in exam_reports:
                lesson_name = (
                    rep.exam.lesson.name
                    if (rep.exam and rep.exam.lesson)
                    else "عمومی / جامع"
                )
                school_exam_avg = round(exam_avg_map.get(rep.exam_id, 0.0) or 0.0, 1)
                passed = (rep.percentage or 0.0) >= pass_threshold
                item_data = {
                    "report": rep,
                    "exam_name": rep.exam.name if rep.exam else "-",
                    "lesson_name": lesson_name,
                    "score": round(rep.score or 0.0, 2),
                    "max_score": round(rep.max_score or 100.0, 2),
                    "percentage": round(rep.percentage or 0.0, 1),
                    "school_exam_avg": school_exam_avg,
                    "rank": rep.rank,
                    "teraze": round(rep.teraze or 0.0, 0) if rep.teraze else None,
                    "passed": passed,
                    "status_label": "قبول" if passed else "نیاز به تلاش بیشتر",
                }
                exam_items.append(item_data)
                lesson_groups[lesson_name].append(item_data)
                total_score_sum += rep.score or 0.0
                total_pct_sum += rep.percentage or 0.0

                prescription = getattr(rep, "adviser_prescription", None)
                if prescription and prescription.action_plan_for_next_exam:
                    adviser_comments.append(
                        {
                            "exam_name": rep.exam.name,
                            "text": prescription.action_plan_for_next_exam,
                        }
                    )

            lesson_summaries = []
            for l_name, items in lesson_groups.items():
                cnt = len(items)
                l_avg_score = round(sum(i["score"] for i in items) / cnt, 2)
                l_avg_pct = round(sum(i["percentage"] for i in items) / cnt, 1)
                l_passed = l_avg_pct >= pass_threshold
                lesson_summaries.append(
                    {
                        "lesson_name": l_name,
                        "exams_count": cnt,
                        "avg_score": l_avg_score,
                        "avg_pct": l_avg_pct,
                        "passed": l_passed,
                        "status_label": "قبول" if l_passed else "نیازمند تقویت",
                    }
                )

            total_exams = len(exam_items)
            overall_avg_score = (
                round(total_score_sum / total_exams, 2) if total_exams else 0.0
            )
            overall_avg_pct = (
                round(total_pct_sum / total_exams, 1) if total_exams else 0.0
            )
            overall_passed = overall_avg_pct >= pass_threshold if total_exams else False

            raw_cards.append(
                {
                    "student": st,
                    "enrolled_classes": list(st.classes.all()),
                    "exam_items": exam_items,
                    "lesson_summaries": lesson_summaries,
                    "total_exams": total_exams,
                    "overall_avg_score": overall_avg_score,
                    "overall_avg_pct": overall_avg_pct,
                    "overall_passed": overall_passed,
                    "pass_status_label": (
                        "قبول و حائز رتبه مطلوب"
                        if overall_passed
                        else ("بدون آزمون" if total_exams == 0 else "نیازمند تلاش بیشتر")
                    ),
                    "adviser_comments": adviser_comments[:3],
                }
            )

        raw_cards.sort(key=lambda c: (c["overall_avg_pct"], c["overall_avg_score"]), reverse=True)
        for rank_idx, card in enumerate(raw_cards, start=1):
            card["overall_rank"] = rank_idx

        return {
            "report_cards": raw_cards,
            "results_count": len(raw_cards),
        }
