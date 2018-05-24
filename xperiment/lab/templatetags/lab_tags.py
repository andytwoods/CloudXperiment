from django import template

from lab.models import LabScientist

register = template.Library()


@register.filter()
def get_lab_list(user):
    ls_list = LabScientist.objects.filter(scientist=user)
    return [item.lab for item in ls_list]