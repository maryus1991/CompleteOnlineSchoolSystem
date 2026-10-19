# apps/exams/tasks.py
from __future__ import annotations

import statistics
from typing import Any

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.tasks import task
from django.utils import timezone

from apps.exams.models import Exam
from apps.questions.models import StudentAnswer
from apps.users.students.models import Student
from apps.reports.models import ExamReport


def _calculate_student_raw_score(exam: Exam, student: Student) -> dict[str, Any]:
    """
    محاسبه نمره خام یک دانش‌آموز.
    پشتیبانی از نمره منفی تستی + نمره دستی تشریحی.
    """
    answers = (
        StudentAnswer.objects
        .filter(exam=exam, student=student)
        .select_related("selected_option", "question")
    )

    total_questions = exam.question.count()
    if total_questions == 0:
        return {
            "total_questions": 0,
            "correct": 0,
            "wrong": 0,
            "unanswered": 0,
            "skipped": 0,
            "uncorrected": 0,
            "raw_score": 0.0,
            "max_score": float(exam.max_score),
        }

    correct = 0
    wrong = 0
    unanswered = 0
    skipped = 0
    uncorrected = 0
    obtained_score = 0.0

    max_possible = (
        exam.question.aggregate(total=Coalesce(Sum("score"), 0.0))["total"]
        or float(exam.max_score)
    )

    negative_factor = 0.0
    if exam.have_negative_score:
        negative_factor = exam.reduce_percent_of_negative_score / 100.0

    for ans in answers:
        q = ans.question
        q_score = float(q.score) if q else 1.0

        if ans.type_of_answer == StudentAnswer.TypeOfAnswer.SKIPPED:
            skipped += 1
            continue

        if ans.type_of_answer == StudentAnswer.TypeOfAnswer.NOT_ANSWERED:
            unanswered += 1
            continue

        # ---------- سوال تستی ----------
        if ans.type_of_answer == StudentAnswer.TypeOfAnswer.OPTION:
            if ans.selected_option and ans.selected_option.is_correct:
                correct += 1
                obtained_score += q_score
            else:
                wrong += 1
                if exam.have_negative_score:
                    obtained_score -= q_score * negative_factor

        # ---------- سوالات تشریحی / تصویری / PDF ----------
        else:
            if ans.corrected == StudentAnswer.TypeOfCorrect.not_corrected:
                uncorrected += 1
            else:
                obtained_score += float(ans.score or 0)
                if ans.score and ans.score >= q_score * 0.7:
                    correct += 1
                elif not ans.score or ans.score <= 0:
                    wrong += 1

    obtained_score = max(0.0, obtained_score)

    if max_possible > 0:
        final_score = (obtained_score / max_possible) * float(exam.max_score)
    else:
        final_score = obtained_score

    return {
        "total_questions": total_questions,
        "correct": correct,
        "wrong": wrong,
        "unanswered": unanswered,
        "skipped": skipped,
        "uncorrected": uncorrected,
        "raw_score": round(final_score, 2),
        "max_score": float(exam.max_score),
    }


def _calculate_percentage(score: float, max_score: float) -> float:
    if max_score <= 0:
        return 0.0
    return round(min(100.0, max(0.0, (score / max_score) * 100)), 2)


def _calculate_taz(score: float, mean: float, std: float, scale: float = 5000.0) -> float:
    """
    فرمول رایج تراز کنکوری:
    تراز = 5000 + 2000 * ((نمره - میانگین) / انحراف معیار)
    """
    if std is None or std < 1e-6:
        return scale
    z = (score - mean) / std
    return round(scale + (2000 * z), 2)


# ---------------------------------------------------------------------------
# تسک‌های اصلی با Django Tasks Framework
# ---------------------------------------------------------------------------

@task()
def calculate_exam_reports(exam_id: int, publish: bool = False) -> dict[str, Any]:
    """
    محاسبه کامل کارنامه همه دانش‌آموزان یک آزمون:
    - تعداد صحیح / غلط / بی‌پاسخ
    - نمره + درصد
    - رتبه
    - تراز

    publish=True → وضعیت را به PUBLISHED تغییر می‌دهد.
    """
    try:
        exam = Exam.objects.get(pk=exam_id)
    except Exam.DoesNotExist:
        return {"error": f"Exam {exam_id} not found"}

    student_ids = list(
        StudentAnswer.objects
        .filter(exam=exam)
        .values_list("student_id", flat=True)
        .distinct()
    )

    if not student_ids:
        return {"message": "هیچ پاسخی برای این آزمون وجود ندارد", "exam_id": exam_id}

    results = []
    scores_for_stats = []

    with transaction.atomic():
        for student_id in student_ids:
            student = Student.objects.get(pk=student_id)
            data = _calculate_student_raw_score(exam, student)

            percentage = _calculate_percentage(data["raw_score"], data["max_score"])
            answered = data["correct"] + data["wrong"]
            answered_pct = (
                round((answered / data["total_questions"]) * 100, 2)
                if data["total_questions"] else 0.0
            )

            report, _ = ExamReport.objects.update_or_create(
                exam=exam,
                student=student,
                defaults={
                    "status": ExamReport.ReportStatus.PENDING,
                    "total_questions": data["total_questions"],
                    "correct_count": data["correct"],
                    "wrong_count": data["wrong"],
                    "unanswered_count": data["unanswered"],
                    "skipped_count": data["skipped"],
                    "uncorrected_count": data["uncorrected"],
                    "score": data["raw_score"],
                    "max_score": data["max_score"],
                    "percentage": percentage,
                    "answered_percentage": answered_pct,
                    "rank": None,
                    "teraze": None,
                    "calculated_at": timezone.now(),
                },
            )
            results.append(report)
            scores_for_stats.append(data["raw_score"])

        # آمار برای تراز
        if len(scores_for_stats) >= 2:
            mean = statistics.mean(scores_for_stats)
            std = statistics.stdev(scores_for_stats)
        else:
            mean = scores_for_stats[0] if scores_for_stats else 0.0
            std = 0.0

        percentages = [r.percentage for r in results]

        if len(percentages) >= 2:
            mean_pct = statistics.mean(percentages)
            std_pct = statistics.stdev(percentages)
        else:
            mean_pct = percentages[0] if percentages else 0.0
            std_pct = 0.0

        exam.average_percentage = round(mean_pct, 2)
        exam.std_percentage = round(std_pct, 2)
        exam.average_score = round(mean, 2)
        exam.std_score = round(std, 2)
        exam.participants_count = len(results)
        exam.stats_calculated_at = timezone.now()
        exam.save(update_fields=[
            "average_percentage",
            "std_percentage",
            "average_score",
            "std_score",
            "participants_count",
            "stats_calculated_at",
        ])

        # رتبه و تراز
        sorted_reports = sorted(results, key=lambda r: r.score, reverse=True)

        for rank, report in enumerate(sorted_reports, start=1):
            taz = _calculate_taz(report.score, mean, std)

            report.rank = rank
            report.teraze = taz
            report.status = (
                ExamReport.ReportStatus.PUBLISHED
                if publish
                else ExamReport.ReportStatus.CALCULATED
            )
            if publish:
                report.published_at = timezone.now()
            report.save(update_fields=["rank", "teraze", "status", "published_at"])

    return {
        "exam_id": exam_id,
        "students_processed": len(results),
        "mean_score": round(mean, 2),
        "std_score": round(std, 2),
        "published": publish,
    }


@task()
def calculate_single_student_report(exam_id: int, student_id: int) -> dict[str, Any]:
    """محاسبه کارنامه فقط برای یک دانش‌آموز (مثلاً بعد از تصحیح دستی)"""
    try:
        exam = Exam.objects.get(pk=exam_id)
        student = Student.objects.get(pk=student_id)
    except (Exam.DoesNotExist, Student.DoesNotExist):
        return {"error": "Exam or Student not found"}

    data = _calculate_student_raw_score(exam, student)
    percentage = _calculate_percentage(data["raw_score"], data["max_score"])
    answered = data["correct"] + data["wrong"]
    answered_pct = (
        round((answered / data["total_questions"]) * 100, 2)
        if data["total_questions"] else 0.0
    )

    report, _ = ExamReport.objects.update_or_create(
        exam=exam,
        student=student,
        defaults={
            "status": ExamReport.ReportStatus.CALCULATED,
            "total_questions": data["total_questions"],
            "correct_count": data["correct"],
            "wrong_count": data["wrong"],
            "unanswered_count": data["unanswered"],
            "skipped_count": data["skipped"],
            "uncorrected_count": data["uncorrected"],
            "score": data["raw_score"],
            "max_score": data["max_score"],
            "percentage": percentage,
            "answered_percentage": answered_pct,
            "calculated_at": timezone.now(),
        },
    )

    return {
        "report_id": report.id,
        "score": report.score,
        "percentage": report.percentage,
    }


@task()
def recalculate_ranks_and_taz(exam_id: int) -> dict[str, Any]:
    """
    فقط رتبه و تراز را دوباره محاسبه می‌کند
    (بعد از تغییر نمره دستی یک یا چند نفر)
    """
    reports = list(
        ExamReport.objects
        .filter(
            exam_id=exam_id,
            status__in=[
                ExamReport.ReportStatus.CALCULATED,
                ExamReport.ReportStatus.PUBLISHED,
            ],
        )
        .order_by("-score")
    )
    if not reports:
        return {"message": "هیچ کارنامه‌ای وجود ندارد"}

    scores = [r.score for r in reports]
    mean = statistics.mean(scores) if len(scores) > 1 else scores[0]
    std = statistics.stdev(scores) if len(scores) > 1 else 0.0

    with transaction.atomic():
        for rank, report in enumerate(reports, start=1):
            report.rank = rank
            report.teraze = _calculate_taz(report.score, mean, std)
            report.save(update_fields=["rank", "teraze"])

    return {
        "exam_id": exam_id,
        "updated": len(reports),
        "mean": round(mean, 2),
        "std": round(std, 2),
    }