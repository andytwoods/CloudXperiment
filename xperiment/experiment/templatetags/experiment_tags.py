from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def underlinebr(value):
    a_list = value.split('_')
    if len(a_list) >= 3:
        result = '</br>'.join(a_list[:3]) + ' ' + ' '.join(a_list[3:])
        return mark_safe(result)
    return mark_safe(value.replace('_', '<br />'))
