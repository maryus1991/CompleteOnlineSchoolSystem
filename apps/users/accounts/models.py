from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from random import randint
from phonenumber_field.modelfields import PhoneNumberField
from .manager import UserManager

class User(AbstractUser):
    """
     User model
    """

    class GenderOfUser(models.TextChoices):
        """
        for detect the gender of User
        """
        MALE = "M", 'مذکر'
        FEMALE = "F", "مونث"

    gender = models.CharField(max_length=255, choices=GenderOfUser, default=GenderOfUser.MALE , verbose_name="جنسیت")
    PhoneNumber = PhoneNumberField(unique=True, verbose_name="شماره", db_index=True)

    private_code = models.CharField(max_length=1000, verbose_name='کد مخفی کاربر', null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="کد otp")
    otp_expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انقضای ")
    is_verified = models.BooleanField(default=True, verbose_name='تایید شماره همراه')
    login_temp = models.PositiveSmallIntegerField(default=0, verbose_name="دفعات ورود")

    USERNAME_FIELD = "PhoneNumber"
    username = None
    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ('-pk',)

    def __str__(self):
        if self.first_name or self.last_login:
            return self.get_full_name()

        return f"{str(self.PhoneNumber).replace(' ', '')}"

    def increase_login_temp(self):
        self.login_temp += 1
        self.save()

    def zero_login_temp(self):
        self.login_temp = 0
        self.save()

    def set_otp(self) -> int:

        self.otp_expiry_date = now() + timedelta(seconds=int(settings.OTP_EXPIRATIONS_SECONDS))
        self.otp = randint(int(settings.OTP_EXPIRATIONS_RANGE_START), int(settings.OTP_EXPIRATIONS_RANGE_END))

        if self.login_temp > settings.LOGIN_TEMP:
            self.is_verified = False
            self.is_active = False
            self.save()

        else:
            self.increase_login_temp()

        return self.otp

    def verify_otp(self, otp: str) -> list:

        if (int(self.otp) == int(otp)) and (self.otp_expiry_date >= now()):
            self.otp = ""
            self.otp_expiry_date = None
            self.is_verified = True
            self.login_temp = 0
            self.private_code = None
            self.save()

            return [200, 'verified']
        elif (int(self.otp) != int(otp)) and (self.otp_expiry_date >= now()):
            return [401, 'کد اعتبار سنجی اشتباه است']
        elif (int(self.otp) == int(otp)) and (self.otp_expiry_date < now()):
            return [402, 'زمان وارد کردن کد تمام شده است لطفا دوباره امتحان فرمایید']