from django import template
from django.utils.safestring import mark_safe
from experiment.models import ExptAnswer
import json

register = template.Library()


@register.simple_tag
def get_answer_count(expt_id):
    result = 0
    if expt_id:
        result = ExptAnswer.objects.filter(expt_id=expt_id, expt_data__has_key='info_duration').count()
    return result


@register.filter
def get_expt_answer(value, arg):
    if value == "{}":
        return ""

    return value.get(arg, "")

@register.filter
def get_expt_answer_xptv1(value, arg):
    if value == "{}":
        return ""
    return value.get(arg, "")

@register.filter
def underlinebr(value):
    a_list = value.split('_')
    if len(a_list) >= 3:
        result = '</br>'.join(a_list[:3]) + ' ' + ' '.join(a_list[3:])
        return mark_safe(result)
    return mark_safe(value.replace('_', '<br />'))
