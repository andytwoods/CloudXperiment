import json
import random
import string
import re

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.defaultfilters import slugify, striptags
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def json_result(request, data):
    response_data = json.dumps(data)
    if 'application/json' in request.META.get('HTTP_ACCEPT_ENCODING', None):
        content_type = 'application/json'
    else:
        content_type = 'text/plain'
    return HttpResponse(response_data, content_type=content_type)


def form_errors_to_json(errors):
    """
    Convert a Form error list to JSON
    """
    # Force error strings to be un-lazied.

    error_summary = {}
    my_errors = {}
    for error in errors.items():
        my_errors.update({error[0]: striptags(error[1]
                                         if strip_tags else error[1])})
    error_summary.update({'error': my_errors})
    print(error_summary,22)
    return error_summary



def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
        # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
        # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value


def get_page(request, items, count_per_page, process_out_of_range=True):
    paginator = Paginator(items, count_per_page)
    page = request.GET.get('page', 1)
    try:
        paginator.object_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginator.object_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginator.object_list = paginator.page(paginator.num_pages)
    except Exception as e:
        print(e)

    if not process_out_of_range:
        if int(page) not in paginator.page_range:
            paginator.object_list.object_list = []

    return paginator


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.sample(chars, length))


def get_email_content(context, template_name):
    return render_to_string(template_name, context).strip()


def send_email(subject, to_emails, context, template_name):
    msg = EmailMessage(subject,
                       render_to_string(template_name, context).strip(),
                       settings.DEFAULT_FROM_EMAIL,
                       to_emails)
    msg.content_subtype = 'html'
    msg.send()

PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )

def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and
                proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip