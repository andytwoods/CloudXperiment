import json

from django.http import HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from allauth.account import app_settings
from allauth.account.forms import SignupForm
from allauth.account.utils import complete_signup

from attachment.models import AttachmentRelationship
from attachment.views import attachment_upload
from .utils import form_errors_to_json, json_result
from scientist.models import Profile
from django.shortcuts import render

def ajax_signup(request, **kwargs):
    if request.is_ajax() and request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            Profile(user=user).save()
            if not hasattr(user, 'backend'):
                user.backend = "django.contrib.auth.backends.ModelBackend"
            ret = complete_signup(request, user,
                                  app_settings.EMAIL_VERIFICATION,
                                  '/')

            data = {'status': 'success', 'next': ret.url}
        else:
            data = form_errors_to_json(form.errors)
        return json_result(request, data)

    return HttpResponseNotAllowed(['POST', ], content_type='application/json')


def home(request, template='home.html', extra_context=None):

    context = {}

    if extra_context:
        context.update(extra_context)

    return render(request, template, context)



@login_required
def upload_avatar(request):
    '''
    Upload avatar
    :param request:
    :return:
    '''
    attachment_list = AttachmentRelationship.objects.filter_attachment(request.user)
    try:
        data = attachment_upload(request, request.user)
        for attachment in attachment_list:
            attachment.delete()
    except Exception as e:
        print(e.message)
    json_data = json.dumps({'status': 'success', 'thumbnail_url': data['url']})
    return HttpResponse(json_data, content_type='application/json')