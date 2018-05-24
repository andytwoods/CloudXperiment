from django.contrib.auth import user_logged_in
from scientist.models import Profile


def check_userprofile(sender, request, user, **kwargs):
    try:
        profile = user.profile
    except:
        Profile(user=user).save()

user_logged_in.connect(check_userprofile)
