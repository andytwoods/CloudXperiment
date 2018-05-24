from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import success
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from allauth.account.signals import user_signed_up
from allauth.account.utils import send_email_confirmation

from allauth.account.models import EmailAddress
from allauth.account import app_settings

from attachment.views import attachment_upload
from balancer.views import rand_from_balancer
from balancer.models import BalanceItem
from core.utils import json_result, generate_password, send_email
from scientist.models import Profile
from .forms import LabForm
from .models import Lab, LabScientist, PaymentRecord, StudyBalancer
from .utils import ROLE_CREATOR


def lab_list(request, template='lab/lab_list.html', extra_context=None):
    context = {}

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def lab_detail(request, lab_id, slug, template='lab/lab_detail.html', extra_context=None):
    lab = get_object_or_404(Lab, id=lab_id)
    if slug != lab.slug:
        return HttpResponseRedirect(reverse_lazy('lab_detail', args=[lab.id, lab.slug]))

    context = {
        'lab': lab,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def add_edit_lab(request, lab_id=None, template='lab/add_edit_lab.html', extra_context=None):
    lab = None
    action = 'Add'
    if lab_id:
        lab = get_object_or_404(Lab, id=lab_id, creator=request.user)
        action = 'Edit'

    form = LabForm(instance=lab)

    if request.method == 'POST':
        form = LabForm(instance=lab, data=request.POST, files=request.FILES)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.creator = request.user
            lab.save()
            lab.add_scientist(request.user.email, request.user, ROLE_CREATOR)
            success(request, _(u'%s has been saved.' % lab.name))

            return HttpResponseRedirect(reverse_lazy('lab_detail', args=[lab.id, lab.slug]))

    context = {
        'form': form,
        'action': action,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def add_member(request):
    lab_id = request.POST.get('lab_id', None)
    member_email = request.POST.get('member_email', None)
    lab = get_object_or_404(Lab, pk=lab_id)

    new_user = None
    temp_password = None
    try:
        user = User.objects.get(email=member_email)
    except User.DoesNotExist:
        temp_password = generate_password(8)
        user = User.objects.create_user(username=member_email, email=member_email, password=temp_password)
        Profile(user=user, is_scientist=True).save()
        if not hasattr(user, 'backend'):
            user.backend = 'django.contrib.auth.backends.ModelBackend'
        user_signed_up.send(sender=user.__class__,
                            request=request,
                            user=user)
        has_verified_email = EmailAddress.objects.filter(user=user,
                                                         verified=True).exists()
        if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.NONE:
            pass
        else:
            if not has_verified_email:
                send_email_confirmation(request, user, signup=False)
        new_user = user

    if lab.labscientist_set.filter(email=member_email, scientist=user).count() > 0:
        result = {'status': 'warning', 'message': 'User already exist'}
    else:
        lab_scientist = LabScientist(lab=lab, email=user.email, scientist=user)
        lab_scientist.save()
        scientist = lab_scientist.scientist
        send_email(
            subject='%s added you to lab %s as a member' % (lab.creator.profile.get_full_name(), lab.name),
            to_emails=[user.email],
            template_name='lab/email/add_member_email.html',
            context={
                'lab': lab,
                'site_url': request.get_host(),
                'new_user': new_user,
                'temp_password': temp_password,
            }
        )
        result = {
            'status': 'success',
            'member_email': member_email,
            'username': scientist.username if scientist else lab_scientist.email,
            'fullname': scientist.profile.get_full_name() if scientist else lab_scientist.email,
            'role': lab_scientist.get_role_display(),
            'url': '/static/images/avator.png',
            'created': lab_scientist.created.strftime('%b. %d, %y, %I:%M %p.'),
        }

    return json_result(request, result)


@login_required
def delete_member(request):
    ls_list = None
    lab_id = request.POST.get('lab_id', None)
    lab = get_object_or_404(Lab, pk=lab_id)
    member_email = request.POST.get('member_email', None)

    if member_email:
        ls_list = LabScientist.objects.filter(Q(lab__id=lab_id),
                                              Q(scientist__email=member_email) | Q(email=member_email))

    if ls_list and len(ls_list) > 0:
        ls_list[0].delete()
        send_email(
            subject='%s removed you from lab %s' % (lab.creator.profile.get_full_name(), lab.name),
            to_emails=[member_email],
            template_name='lab/email/remove_member_email.html',
            context={
                'lab': lab,
                'site_url': request.get_host(),
            }
        )
        result = {'status': 'success', 'member_email': member_email}
    else:
        result = {'status': 'error', 'message': 'The user does not exist in the lab'}

    return json_result(request, result)


@login_required
def upload_logo(request):
    '''
    Upload logo
    :param request:
    :return:
    '''

    lab_id = request.GET.get('lab_id')
    try:
        lab = Lab.objects.get(pk=lab_id)
        data = attachment_upload(request, lab)
        lab.logo = data['url']
        lab.save()
        result = {'status': 'success', 'thumbnail_url': lab.logo}
    except Lab.DoesNotExist:
        result = {'status': 'error', 'message': 'The lab does not exist'}
    except Exception as e:
        result = {'status': 'error', 'message': e.message}
    return json_result(request, result)


@login_required
def payment(request, lab_id, template='lab/payment.html', extra_context=None):
    lab = get_object_or_404(Lab, id=lab_id, creator=request.user)

    #TODO: Add paypal form

    context = {
        'lab': lab,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def payment_complete(request, lab_id):
    amount = float(request.POST.get('amount'))
    lab = get_object_or_404(Lab, id=lab_id)
    lab.balance += amount
    lab.save()
    PaymentRecord(lab=lab, scientist=request.user, amount=amount).save()
    return HttpResponseRedirect(reverse_lazy('lab_detail', args=[lab.id, lab.slug]))



@login_required
def manage_orderings(request, lab_id, template='lab/balancer.html', extra_context=None):
    context = construct_table_info(lab_id)
    context['url'] = request.scheme + '://' + request.get_host() + '/balance/'
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def construct_table_info(lab_id):
    order_list = serializers.serialize('json', StudyBalancer.objects.filter(lab_id=lab_id).order_by('-created'),
                                       fields=('name', 'slug', 'randomness'))

    print(order_list)

    return {'order_list': order_list}


@login_required
def delete_order(request, lab_id):
    order_ids = request.POST.getlist('order_ids[]', None)

    if order_ids and len(order_ids) > 0:
        try:
            StudyBalancer.objects.filter(pk__in=order_ids, lab_id=lab_id).delete()
            delete_balanceItems(lab_id, order_ids)
            result = {
                'status': 'success',
                'objects': []
            }
            result.update(construct_table_info(lab_id))
        except Exception as e:
            result = {
                'status': 'error',
                'message': e
            }
    else:
        result = {
            'status': 'error',
            'message': 'Parameters order ids can not be empty'
        }

    return json_result(request, result)


def delete_balanceItems(lab_id, order_ids):
    delete_list = []
    for id in order_ids:
        delete_list.append(balance_item_id_generate(lab_id, id))
    BalanceItem.objects.filter(group_id__in=delete_list).delete()


@login_required
def balancer_update(request, lab_id):

    batch_pk = request.POST.get('batch_id', None)
    randomness = request.POST.get('randomness', None)

    if batch_pk and randomness:
        try:
            result = {
                'status': 'success',
                'items': []
            }

            balance_item = StudyBalancer.objects.get(lab_id=lab_id, pk=batch_pk)
            balance_item.randomness = float(randomness)
            balance_item.save()

        except Exception as e:
            result = {
                'status': 'error',
                'message': e
            }
    else:
        result = {
            'status': 'error',
            'message': 'batch id can not be empty'
        }

    return json_result(request, result)


@login_required
def balancer_add(request, lab_id):
    batch_name = request.POST.get('batch_name', None)

    if batch_name:
        try:
            result = {
                'status': 'success',
                'items': []
            }

            balance_item, created = StudyBalancer.objects.get_or_create(lab_id=lab_id, name=batch_name)
            if created:
                balance_item.save()

            result.update(construct_table_info(lab_id))

        except Exception as e:
            result = {
                'status': 'error',
                'message': e
            }
    else:
        result = {
            'status': 'error',
            'message': 'batch order items can not be empty'
        }

    return json_result(request, result)


def balance_item_id_generate(lab_id, balance_id):
    return lab_id + '__' + balance_id


@login_required
def balancer_edit(request, lab_id, balance_id):
    balance_item_id = balance_item_id_generate(lab_id, balance_id)
    return redirect('balancer', group_id=balance_item_id)


def balancer_url(request, slug):

    found = StudyBalancer.objects.prefetch_related('lab').get(slug=slug)

    balance_item_id = balance_item_id_generate(str(found.lab.pk), str(found.id))
    chosen = rand_from_balancer(balance_item_id, found.randomness)

    if chosen is None:
        return HttpResponse('You need to specify some urls to balance over.')

    if 'http' not in chosen:
        chosen = 'https://' + chosen

    return redirect(chosen)
