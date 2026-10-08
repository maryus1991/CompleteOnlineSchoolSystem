from .models_fields import JalaliDateTime
from django.utils import timezone

def datetime2jalali(value=None):
    if value is None:
        value = timezone.localtime(timezone.now())
    else:
        value = timezone.localtime(value)

    return JalaliDateTime.fromgregorian(datetime=value)