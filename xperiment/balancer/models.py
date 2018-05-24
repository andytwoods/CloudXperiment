from model_utils.models import TimeStampedModel
from django.db import models


class BalanceItem(TimeStampedModel):
    group_id = models.CharField(max_length=255, verbose_name='groupId')
    ordering = models.CharField(max_length=255, verbose_name='order')
    count = models.IntegerField(default=0, verbose_name='count')
