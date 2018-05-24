from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.utils.html_parser import HTMLParser


def get_subject(label, context):
    html_parser = HTMLParser.HTMLParser()
    subject = ''.join(render_to_string('email/%s/subject.txt' % (label, ), context).splitlines())
    return html_parser.unescape(subject)


def get_body(label, context):
    return render_to_string('email/%s/body.html' % (label, ), context)


def extra_context(context):
    context.update({
        'current_site': 'https://%s' % Site.objects.get_current().name,
    })
    return context


def create_message(slug, context, from_email=None, to=None, headers=None):
    context = extra_context(context)

    if not from_email:
        try:
            from_email = context['sender'].email
        except Exception as e:
            raise Exception('Please specify a sender[%s]' % e.message)

    if not to:
        try:
            to = (context['recipient'].email, )
        except Exception as e:
            raise Exception('Please specify a recipient[%s]' % e.message)

    if context['is_render']:
        html_content = get_body(slug, context)
        text_content = strip_tags(html_content)
    else:
        html_content = context['content']
        text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(subject=get_subject(slug, context), body=text_content, from_email=from_email,
                                     to=to, headers=headers)
    message.attach_alternative(html_content, 'text/html')

    return message