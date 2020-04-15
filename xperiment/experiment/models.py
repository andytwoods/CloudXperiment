from json import loads, JSONDecodeError

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from core.utils import unique_slugify
from lab.models import Lab
from .utils import get_expt_uuid


def default_headers():
    return "{'headers': []}"

def default_url_params():
    return ''


class ExptInfo(TimeStampedModel):
    expt_id = models.CharField(primary_key=True, max_length=50, default=get_expt_uuid, verbose_name=_(u'Experiment Id'))
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=50, verbose_name=_(u'Experiment Name'))
    participant_count = models.IntegerField(default=200, verbose_name=_(u'Participant count'))
    lab = models.ForeignKey(Lab, verbose_name=_(u'Laboratory'), null=True, on_delete=models.SET_NULL)
    is_paid = models.BooleanField(default=False)
    is_password = models.BooleanField(default=False, verbose_name=_(u'Need password?'))
    is_encrypt = models.BooleanField(default=False, verbose_name=_(u'Encrypt Upload Files?'))
    is_publish = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=50, null=True, blank=True, verbose_name=_(u'Secret Key'))
    is_delete = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    live = models.BooleanField(default=True)

    alias = models.ForeignKey('self', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    url_params = models.TextField(default=default_url_params)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        slug = '%s' % self.name
        unique_slugify(self, value=slug)
        super(ExptInfo, self).save(**kwargs)

    def get_absolute_url(self):

        if self.alias is not None:
            slug = self.alias.slug
        else:
            slug = self.slug
        path = reverse('experiment_run_short_url', args=[slug])

        return self.add_url_params(path)

    def json_url_params(self):
        try:
            return loads(self.url_params)
        except (JSONDecodeError, TypeError):
            return {}

    def add_url_params(self, url):

        url_params = self.json_url_params()

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


class QuestionOrder(TimeStampedModel):
    expt_info = models.ForeignKey(ExptInfo, null=True, on_delete=models.SET_NULL)
    order = models.CharField(max_length=255, verbose_name=_(u'Order'))
    number = models.PositiveIntegerField(default=0, verbose_name=_(u'Number'))
