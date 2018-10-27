from django.db import models

from user.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(verbose_name='company', max_length=80, blank=True)
    website = models.URLField(verbose_name='website', max_length=200, blank=True)
    sm8_uuid = models.CharField(verbose_name='sm8 uuid', max_length=80, blank=True)
    access_token = models.CharField('Access token', max_length=80)
    refresh_token = models.CharField('Refresh token', max_length=80)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}, {}".format(self.user.email, self.company)