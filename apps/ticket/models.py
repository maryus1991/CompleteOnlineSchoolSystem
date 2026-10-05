from cProfile import label

from django.db import models
from apps.common.models import BaseModel
from django_ckeditor_5.fields import CKEditor5Field
from apps.users.accounts.models import User
from apps.common.file_storage_script_for_model import UploadPath


class Ticket(BaseModel):
    class TicketPriority(models.TextChoices):
        low = 'پایین', 'پایین'
        mid = 'متوسط', 'متوسط'
        high = 'بالا', 'بالا'
        huge = 'فوری', 'فوری'

    class TicketStatus(models.TextChoices):
        cancelled = 'کنسل شده', 'کنسل شده'
        fixed = 'حل شده', 'حل شده'
        awating_admin = 'در انتظار پاسخ ادمین', 'در انتظار پاسخ ادمین'
        awating_user = 'در انتظار پاسخ کاربر', 'در انتظار کاربر'

    name = models.CharField(max_length=500, verbose_name='موضوع', db_index=True)
    user = models.ForeignKey(User, related_name='tickets', on_delete=models.PROTECT, verbose_name='درخواست دهنده', db_index=True)
    description = models.TextField(verbose_name="توضیحات ")
    file = models.FileField(verbose_name='پیوست', upload_to=UploadPath("tickets/"), null=True, blank=True)
    priority = models.CharField(verbose_name='اهمیت', choices=TicketPriority, max_length=255)
    status = models.CharField(verbose_name='وضعیت', choices=TicketStatus, max_length=255)

    class Meta:
        ordering = ['-id']
        verbose_name = 'تیکت '
        verbose_name_plural = 'تیکت  ها'

    def __str__(self):
        return f'{self.name} - {self.user.PhoneNumber}'


class TicketChat(BaseModel):
    ticket = models.ForeignKey(Ticket, related_name='chats', on_delete=models.CASCADE, verbose_name='تیکت')
    admin = models.ForeignKey(User, related_name='tickets_admin', null=True, blank=True, on_delete=models.PROTECT, verbose_name='ادمین', db_index=True)
    is_read_by_admin = models.BooleanField(verbose_name='خوانده شده توسط ادمین', default=False)
    is_read_by_user = models.BooleanField(verbose_name='خوانده شده توسط کاربر', default=False)
    admin_message = CKEditor5Field(verbose_name="پیام", null=True, blank=True)
    user_message = models.TextField(verbose_name="پیام", null=True, blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'پیام تیکت  '
        verbose_name_plural = 'پیام های تیکت'

    def __str__(self):
        return f'{self.id} - {self.ticket.name} - {self.ticket.user.PhoneNumber}'