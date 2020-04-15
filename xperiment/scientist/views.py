from django.urls import reverse_lazy

from core.utils import json_result
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import success
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _

from .forms import ProfileForm
from lab.models import LabScientist
from .models import Profile


def scientist_list(request, template='scientist/scientist_list.html', extra_context=None):
    context = {}

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def scientist_detail(request, scientist_name, template='scientist/scientist_detail.html', extra_context=None):
    scientist = get_object_or_404(User, username=scientist_name)

    context = {
        'scientist': scientist,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def update_profile(request, template='scientist/update_profile.html', extra_context=None):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(instance=profile, data=request.POST, files=request._files)
        if form.is_valid():
            profile = form.save()
            return HttpResponseRedirect(reverse_lazy('scientist_detail', args=[profile.user.username]))

    context = {
        'form': form,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def api_contact(request):

    result = []
    q = request.GET.get('q', None)
    user = request.user

    if q:
        user_list = User.objects.filter(Q(username__icontains=q) | Q(email__icontains=q)).exclude(
            Q(id=user.id) | Q(is_staff=True))


        for user in user_list:
            result.append(
                {
                    'id': user.email,
                    'avatar': '',
                    'display_name': user.username,
                    'email': user.email
                }
            )
    return json_result(request, result)
