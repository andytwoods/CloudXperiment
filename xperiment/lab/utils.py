from django.utils.translation import ugettext_lazy as _


ROLE_CREATOR = 1
ROLE_ADMIN = 2
ROLE_MEMBER = 3

ROLE_CHOICES = (
    (ROLE_CREATOR, _(u'Creator')),
    (ROLE_ADMIN, _(u'Admin')),
    (ROLE_MEMBER, _(u'Member')),
)