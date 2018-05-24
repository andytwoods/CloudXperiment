from django import template
from django.template.loader import render_to_string

from attachment.models import AttachmentRelationship

register = template.Library()


@register.simple_tag
def avatar(user, size=80, **kwargs):
    attachment_list = AttachmentRelationship.objects.filter_attachment(user)

    context = dict(kwargs, **{
        'user': user,
        'url': attachment_list[0].file.url if attachment_list and len(attachment_list) > 0 else '',
        'alt': user.profile.get_full_name(),
        'size': size,
    })

    return render_to_string('avatar/avatar_tag.html', context)