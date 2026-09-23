import jdatetime

from django.conf import settings
from django_jalali.db import models as jalali_models


class JalaliDateTime(jdatetime.datetime):
    """
    Jalali datetime که نحوه نمایش آن از settings کنترل می‌شود.
    """

    def __str__(self):
        date_format =  settings.JALALI_DISPLAY["DATETIME_FORMAT"]

        return self.strftime(date_format)


class BaseJalaliDateTimeField(jalali_models.jDateTimeField):
    """
    jDateTimeField با نمایش سفارشی برای Template.
    """

    @classmethod
    def parse_date(cls, datetime_obj):
        value = super().parse_date(datetime_obj)

        if value is None:
            return None

        if isinstance(value, JalaliDateTime):
            return value

        return JalaliDateTime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond,
            tzinfo=value.tzinfo,
        )