from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=20, blank=True, null=True)
    fullname = models.CharField(max_length=255, blank=True, null=True)
    # TODO Address field
    website = models.URLField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    is_scientist = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.email

    def get_full_name(self):
        return self.fullname if self.fullname else self.user.username

    def get_absolute_url(self):
        return reverse('scientist_detail', args=[self.user.username])


def check_userprofile(sender, request, user, **kwargs):
    try:
        profile = user.profile
    except:
        Profile(user=user).save()


user_logged_in.connect(check_userprofile)