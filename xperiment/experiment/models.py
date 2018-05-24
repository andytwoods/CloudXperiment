from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from core.utils import unique_slugify
from lab.models import Lab
from .utils import get_expt_uuid


def default_headers():
    return {'headers': []}

def default_url_params():
    return {}


class ExptInfo(TimeStampedModel):
    expt_id = models.CharField(primary_key=True, max_length=50, default=get_expt_uuid, verbose_name=_(u'Experiment Id'))
    creator = models.ForeignKey(User, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=50, verbose_name=_(u'Experiment Name'))
    participant_count = models.IntegerField(default=200, verbose_name=_(u'Participant count'))
    lab = models.ForeignKey(Lab, verbose_name=_(u'Laboratory'))
    is_paid = models.BooleanField(default=False)
    is_password = models.BooleanField(default=False, verbose_name=_(u'Need password?'))
    is_encrypt = models.BooleanField(default=False, verbose_name=_(u'Encrypt Upload Files?'))
    is_publish = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=50, null=True, blank=True, verbose_name=_(u'Secret Key'))
    expt_headers = JSONField(default=default_headers)

    xpt2_xml = models.CharField(blank=True, max_length=255, verbose_name=_(u'file name for xml script'))

    is_delete = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    live = models.BooleanField(default=True)

    alias = models.ForeignKey('self', default=None, null=True, blank=True)
    url_params = JSONField(default=default_url_params)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        slug = '%s' % self.name
        unique_slugify(self, value=slug)
        super(ExptInfo, self).save(**kwargs)

    def xpt_version(self):
        return self.xperiment_version

    def get_absolute_url(self):

        if self.alias is not None:
            slug = self.alias.slug
        else:
            slug = self.slug
        path = reverse('experiment_run_short_url', args=[slug])

        return self.add_url_params(path)


    def add_url_params(self, url):
        url_params = self.url_params

        if self.alias is not None:
            copy_url_params = self.alias.url_params.copy()
            copy_url_params.update(url_params)
            url_params = copy_url_params
            url_params['exptId'] = self.expt_id

        url_params_list = []

        for key, val in url_params.items():
            url_params_list.append(key + "=" + str(val))

        if len(url_params_list) == 0:
            return url

        url_params_str = '&'.join(url_params_list)

        if '?' not in url:
            url_params_str = '?' + url_params_str
        else:
            url_params_str = '&' + url_params_str

        return url + url_params_str


    def get_cdn_url(self):
        if self.alias is not None:
            expt_id = self.alias.expt_id
        else:
            expt_id = self.expt_id

        url_params = {
            'exptId':self.expt_id,
            'expt_info': self.slug,
        }

        url = settings.CDN_URL + '/' + expt_id + '/index.html?' + urlencode(url_params)

        return self.add_url_params(url)


class ExptAnswer(TimeStampedModel):
    user = models.ForeignKey(User, null=True, blank=True)
    client_ip = models.CharField(max_length=255, null=True, blank=True)
    uuid = models.CharField(max_length=36, verbose_name=_(u'SJ id'))
    expt_id = models.CharField(max_length=50, default='', verbose_name=_(u'Experiment Id'))
    between_sjs_id = models.CharField(default='', max_length=100, blank=True, null=True)
    time_start = models.DateTimeField(null=True, blank=True)
    time_zone = models.CharField(default='', max_length=10, blank=True, null=True)
    time_stored = models.DateTimeField(blank=True, null=True)
    expt_data = JSONField(verbose_name=_(u'Experiment Data'), null=True, blank=True, default=dict)
    device_uuid = models.CharField(max_length=32, unique=True, blank=True, null=True)
    order = models.CharField(max_length=255, blank=True, null=True)


class QuestionOrder(TimeStampedModel):
    expt_info = models.ForeignKey(ExptInfo)
    order = models.CharField(max_length=255, verbose_name=_(u'Order'))
    number = models.PositiveIntegerField(default=0, verbose_name=_(u'Number'))
