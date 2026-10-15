
from django import template

register = template.Library()


@register.filter
def get_student_meeting_url(live_class, student):
    if not live_class or not student:
        return ""

    return live_class.get_student_meeting_url(student) or ""