from uuid import uuid4

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel

from core.utils import unique_slugify

from .utils import ROLE_CHOICES, ROLE_MEMBER


class Lab(TimeStampedModel):
    creator = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    # TODO Address field
    website = models.URLField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    logo = models.URLField(max_length=1024, null=True, blank=True)
    balance = models.FloatField(default=0)

    def __unicode__(self):
        return self.name

    @property
    def scientists(self):
        return self.labscientist_set.all()

    def add_scientist(self, email, scientist, role=ROLE_MEMBER):
        try:
            ls = LabScientist.objects.get(lab=self, email=email, scientist=scientist)
            ls.role = role
        except LabScientist.DoesNotExist:
            ls = LabScientist(lab=self, email=email, scientist=scientist, role=role)

        ls.save()

    def save(self, **kwargs):
        slug = '%s' % (self.name)
        unique_slugify(self, slug)
        super(Lab, self).save(**kwargs)

    def get_absolute_url(self):
        return reverse('lab_detail', args=[self.id, self.slug])

    def scientist_belong_this(self, user):
        return self.labscientist_set.filter(scientist = user).count() > 0


class LabScientist(TimeStampedModel):
    role = models.IntegerField(choices=ROLE_CHOICES, default=ROLE_MEMBER)
    lab = models.ForeignKey(Lab)
    email = models.EmailField()
    scientist = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        unique_together = ('lab', 'email', 'scientist')

    def __unicode__(self):
        return self.email


class StudyBalancer(TimeStampedModel):
    lab = models.ForeignKey(Lab)
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, default=uuid4().hex)
    randomness = models.FloatField(default=.2)


class PaymentRecord(TimeStampedModel):
    lab = models.ForeignKey(Lab, verbose_name=_(u'Lab'))
    scientist = models.ForeignKey(User, verbose_name=_(u'Scientist'))
    amount = models.FloatField(default=0, verbose_name=_(u'Amount'))
    description = models.TextField(verbose_name=_(u'Description'), max_length=1024, null=True, blank=True)
