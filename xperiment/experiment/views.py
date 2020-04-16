import hmac
import json
from base64 import b64encode
from datetime import datetime, timedelta
from hashlib import sha1
from json import dumps

import boto3
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.template.defaultfilters import urlencode
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from core.utils import get_page, json_result, get_client_ip
from lab.models import LabScientist, Lab
from .forms import RenameForm, ExptForm_v2
from .models import ExptInfo, QuestionOrder


def experiment_list(request, template='experiment/experiment_list.html', extra_context=None):
    if request.user.is_authenticated:
        experiments = ExptInfo.objects.filter(creator=request.user, is_delete=False).order_by('-created')
    else:
        experiments = ExptInfo.objects.all().order_by('-created')
    paginator = get_page(request, experiments, 20)

    context = {
        'paginator': paginator,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def experiment_manage_archived(request, lab_id, template='experiment/experiment_manage.html', extra_context=None):
    return experiment_manage(request, lab_id, 'archived', template, extra_context)


@login_required
def experiment_manage_command(request, lab_id):
    lab = get_object_or_404(Lab, id=lab_id)
    if not lab.scientist_belong_this(request.user):
        raise Http404
    action = request.POST.get('what', '')
    expt_id = request.POST.get('id', '')

    if expt_id == '':
        raise Http404

    try:
        experiment = ExptInfo.objects.get(lab__id=lab_id, expt_id=expt_id)
    except ObjectDoesNotExist as e:
        raise Http404

    try:
        if action == 'lock_toggle':
            experiment.locked = not experiment.locked
            experiment.save()
            return json_result(request, {'status': 'success',
                                         'icon': 'icon-lock' if experiment.locked else 'icon-unlock'})

        elif action == 'archive_toggle':
            experiment.archived = not experiment.archived
            experiment.save()
            return json_result(request, {'status': 'success',
                                         'icon': 'icon-archive' if experiment.archived else 'icon-bolt'})

        elif action == 'live_toggle':
            experiment.live = not experiment.live
            experiment.save()
            return json_result(request, {'status': 'success',
                                         'icon': 'icon-bolt' if experiment.live else 'icon-archive'})


    except Exception:
        pass

    return json_result(request, {'status': 'fail'})


@login_required
def experiment_manage_archived(request, lab_id, template='experiment/experiment_manage.html', extra_context=None):
    return experiment_manage(request, lab_id, 'archived', template, extra_context)


@login_required
def experiment_manage(request, lab_id, filtered=None, template='experiment/experiment_manage.html', extra_context=None):
    lab = get_object_or_404(Lab, id=lab_id)

    if not lab.scientist_belong_this(request.user):
        raise Http404

    if filtered == 'archived':
        experiments = ExptInfo.objects.filter(lab__id=lab_id, is_delete=False, archived=True).order_by('-created')
    elif filtered == 'discarded':
        experiments = ExptInfo.objects.filter(lab__id=lab_id, is_delete=True, archived=False).order_by('-created')
    else:
        experiments = ExptInfo.objects.filter(lab__id=lab_id, is_delete=False, archived=False).order_by('-created')

    paginator = get_page(request, experiments, 20)

    context = {
        'URL_PREFIX': request.build_absolute_uri('/')[:-1],
        'lab': lab,
        'paginator': paginator,
        'filter': filtered
    }

    if extra_context:
        context.update(extra_context)

    return render(request, template, context)


@login_required
def see_results(request, expt_id):
    extra_context = {
        'save': False,
        'bucket_url': settings.AWS_BUCKET_LOCATION + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '-data/',
        'type': 'data',
    }

    return experiment_edit(request, expt_id, extra_context=extra_context)


@login_required
def experiment_edit(request, expt_id, template='experiment/experiment_create_question.html', extra_context=None):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if expt_info.alias:
        expt_info = expt_info.alias
    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404

    if request.method == 'POST':
        expt_info.is_publish = True
        expt_info.save()
        return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab.id]))

    context = {

        'expt_info': expt_info,
        'access_key': settings.AWS_ACCESS_KEY_ID,
        'bucket_url': settings.AWS_BUCKET_LOCATION + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '/',
        'expt_id': expt_id,
        'type': 'experiment',
    }

    if extra_context:
        context.update(extra_context)

    return render(request, template, context)


@login_required
def experiment_detail(request, expt_id, slug, template='experiment/experiment_detail.html', extra_context=None):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if slug != expt_info.slug:
        return HttpResponseRedirect(reverse_lazy('experiment_detail', args=[expt_info.expt_id, expt_info.slug]))

    context = {
        'expt_info': expt_info,
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def generate_context(request, expt_info, extra_context):
    if request.user.is_authenticated:
        user_id = request.user.id
    else:
        user_id = None

    expt_id = request.GET.get('exptId', expt_info.expt_id)

    context = {
        'one_key': None,
        'client_ip': get_client_ip(request),
        'user_id': user_id,
        'expt_info': expt_info,
        'overSJs': get_question_order(expt_id),
    }

    if extra_context:
        context.update(extra_context)

    return context


def experiment_run_short_url(request, slug):
    expt = get_object_or_404(ExptInfo, slug=slug)

    aliased = request.GET.get('exptId', None)
    if aliased:
        aliased_study = ExptInfo.objects.get(expt_id=aliased)
        if aliased_study.live is False:
            return HttpResponse('Sorry, this study has been disabled', content_type="application/json")

    if expt.live is False:
        return HttpResponse('Sorry, this study has been disabled', content_type="application/json")
    return experiment_run(request, expt.expt_id)


def experiment_run(request, expt_id, extra_context=None):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    context = generate_context(request, expt_info, extra_context)
    return expt_run_v2(context, expt_info, request)


@login_required
def experiment_delete(request):
    try:
        expt_ids = request.POST.getlist('expt_id', [])
        expt_info_list = ExptInfo.objects.filter(expt_id__in=expt_ids, creator=request.user)

        if expt_info_list and len(expt_info_list) > 0:
            for expt_info in expt_info_list:
                delete_s3_dir(expt_info)
                expt_info.delete()
            result = {'status': 'success'}
        else:
            result = {'status': 'fail', 'reason': 'experiment info does not exist'}
    except Exception as e:

        result = {'status': 'fail', 'reason': ''}
    return json_result(request, result)


@login_required
def experiment_attachment_delete_all(request):
    try:
        expt_id = request.POST.get('expt_id')
        expt_info = ExptInfo.objects.get(expt_id=expt_id, is_delete=False)
        if not expt_info.lab.scientist_belong_this(request.user):
            raise Http404
        expt_info.exptinfoattachment_set.all().delete()
        result = {'status': 'success'}
    except Exception as e:
        result = {'status': 'fail', 'reason': e.message}
    return json_result(request, result)


def get_question_order(expt_id):
    try:
        question_order = QuestionOrder.objects.filter(expt_info__pk=expt_id).earliest('number')
        result = question_order.order
        question_order.number += 1
        question_order.save()

    except Exception as e:
        result = ''

    return result


def _process_answer_xml_verify(request, expt_id):
    if request.user.is_staff:
        result = True
    elif expt_id:
        try:
            expt_info = ExptInfo.objects.get(expt_id=expt_id)
            if expt_info.lab.scientist_belong_this(request.user):
                result = True
            else:
                result = False
        except ExptInfo.DoesNotExist:
            result = False
    else:
        result = False

    return result


def tab_sep_to_dict(txt):
    d = dict()

    for keyval in txt.split("\t"):

        _list = keyval.split(":")

        if len(_list) == 2:
            d[_list[0]] = _list[1]

    if len(d.keys()) == 0:
        return None

    return d


@login_required
def experiment_order_delete(request, expt_id):
    """
    Ajax delete experiment order

    """

    order_ids = request.POST.getlist('order_ids[]', None)

    if order_ids and len(order_ids) > 0:
        try:
            expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
            order_list = QuestionOrder.objects.filter(pk__in=order_ids, expt_info=expt_info)
            for order in order_list:
                order.delete()
            result = {
                'status': 'success',
            }
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


@login_required
def experiment_order_batch_modify_order(request, expt_id):
    result = None

    try:
        rows = json.loads(request.POST.get('modify_order[]'))

        expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)

        questions = QuestionOrder.objects.filter(expt_info__pk=expt_id)

        for row in rows:
            for q in questions:
                if q.order == row[u'cond']:
                    q.number = row[u'count']
                    q.save()

    except Exception as e:
        result = {
            'status': 'error',
            'message': e
        }

        if result is not None:
            result = {
                'status': 'success',
                'objects': []
            }
    return json_result(request, result)


@login_required
def reset_question_order_count(request, expt_id):
    result = None

    try:
        for question_order in QuestionOrder.objects.filter(expt_info__pk=expt_id):
            question_order.number = 0
            question_order.save()
            result = {
                'status': 'success',
                'objects': []
            }
    except Exception as e:
        result = {
            'status': 'error',
            'message': e
        }

    return json_result(request, result)


@login_required
def experiment_order_batch_add(request, expt_id):
    """
    Ajax add experiment order

    """

    batch_order = request.POST.get('batch_order', None)

    if batch_order:
        try:
            result = {
                'status': 'success',
                'objects': []
            }
            expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
            batch_order = batch_order.split('\n')
            for order in batch_order:
                if str.strip(order):
                    question_order, created = QuestionOrder.objects.get_or_create(expt_info=expt_info, order=order)
                    result['objects'].append({
                        'id': question_order.pk,
                        'order': question_order.order,
                        'created': created
                    })
        except Exception as e:
            result = {
                'status': 'error',
                'message': e
            }
    else:
        result = {
            'status': 'error',
            'message': 'Parameters batch order can not be empty'
        }

    return json_result(request, result)


def experiment2_run_expt(request, expt, extra_content=None):
    context = generate_context(request, expt, extra_content)
    return expt_run_v2(context, expt, request)


def expt_run_v2(initial_context, expt_info, request):
    initial_context['ip'] = urlencode(initial_context['client_ip'])
    initial_context.pop('expt_info', None)
    initial_context.pop('client_ip', None)

    url_params = []
    for item in initial_context:
        _val = str(initial_context[item])
        if len(_val) > 0 and _val != 'None':
            url_params.append(item + "=" + _val)

    my_url = settings.AWS_BUCKET_LOCATION + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '/' \
             + expt_info.expt_id + '/index.html?' + "&".join(url_params)

    return render(request, "experiment/experiment_run_new_v2.html", {'url': my_url})


def get_experiment_file(request, expt_id, filename):
    url = settings.AWS_BUCKET_LOCATION + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '/' + expt_id + '/' + filename
    return HttpResponseRedirect(url)


@login_required
def create(request, lab_id, template='experiment/experiment_create.html', extra_context=None):
    expt_info = None

    if request.method == 'POST':

        lab_id = request.POST.get('lab_id', None)
        lab = get_object_or_404(Lab, id=lab_id)

        alias_id = request.POST.get('alias_id', None)
        if alias_id:
            alias = get_object_or_404(ExptInfo, expt_id=alias_id)
        else:
            alias = None

        creator = request.user

        for nam in request.POST.get('name', '').split(","):
            expt_info = ExptInfo(creator=creator,
                                 name=nam,
                                 lab=lab
                                 )
            if alias:
                expt_info.alias = alias

            expt_info.save()

        return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab.id]))

    else:

        ls_list = LabScientist.objects.filter(scientist=request.user)
        lab = ls_list[0].lab
        for item in ls_list:
            if str(item.lab.pk) == lab_id:
                lab = item.lab

        es_list = ExptInfo.objects.filter(lab=lab)

        context = {
            'lab': lab,
            'ls_list': ls_list,
            'es_list': es_list
        }
    if extra_context:
        context.update(extra_context)

    return render(request, template, context)


@login_required
def upload_experiment_attachment(request, expt_info):
    u_file = request.FILES['file']
    content_type = u_file.content_type
    attachment_name = request.GET.get('attachment_name', u_file.name)

    return json_result(request, {'status': 'success', 'xptFile': 'true'})


@login_required
def sign_s3(request):
    keys = request.POST.getlist('keys[]')
    types = request.POST.getlist('types[]')
    tags = request.POST.getlist('tags[]')

    signed = []

    for key, _type, tag in zip(keys, types, tags):
        policy = {
            "expiration": (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            "conditions": [
                {"bucket": settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME},
                {"acl": "public-read"},
                ["eq", "$key", key],
                ["starts-with", "$Content-Type", _type],
            ]
        }

        encoded_policy = b64encode(dumps(policy).encode('utf-8'))
        my_hmac = hmac.new(settings.AWS_SECRET_ACCESS_KEY.encode('utf-8'), encoded_policy, sha1).digest()
        signed_policy = b64encode(my_hmac)

        signed.append(
            {
                "tag": tag,
                "policy": encoded_policy.decode("ASCII").replace("\n", ""),
                "signature": signed_policy.decode("ASCII").replace("\n", ""),
            })

    return HttpResponse(dumps(signed), content_type="application/json")


@login_required
def download_zip(request, expt_id, type, template='experiment/download_zip.html'):
    is_data_bucket = type == 'data'

    bucket = getbucket(data_bucket=is_data_bucket)
    keys = bucket.objects.filter(Prefix=expt_id + '/')

    s3 = boto3.client('s3')

    extra = '-data' if is_data_bucket else ''
    bucket_name = settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + extra

    files = []
    for key in keys:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key.key
            }
        )

        if settings.ON_DEV_SERVER:
            url = url.replace('https', 'http')


        files.append({key.key: url})

    context = {'files': files,
               'dir': settings.AWS_BUCKET_LOCATION + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '/'}

    return render(request, template, context)


@login_required
def experiment_rename(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if request.method == 'POST':
        form = RenameForm(user=request.user, instance=expt_info, data=request.POST, files=request.FILES)
        if form.is_valid():
            expt_info = form.save(commit=False)
            expt_info.save()
            return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab_id]))
    else:
        form = ExptForm_v2()

        context = {
            'old_name': expt_info.name,
            'form': form,
        }

    template = 'experiment/experiment_rename.html'
    return render(request, template, context)


@login_required
def experiment_params(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if request.method == 'POST':
        pretty_params = request.POST.get('pretty_params', '')
        errs = []
        params = {}

        if len(pretty_params) > 0:
            for line in pretty_params.split("\n"):
                key_val = line.split('=')
                if len(key_val) != 2:
                    errs.append('cannot add this key+value as not formatted correctly (x=y): ' + line)
                else:
                    params[key_val[0]] = key_val[1]

        expt_info.url_params = dumps(params)
        expt_nam = expt_info.name

        if len(errs) > 0:
            messages.error(request, expt_nam + ': ' + '/n'.join(errs))

        messages.success(request, expt_nam + ': added these url params: ' + dumps(params))

        expt_info.save()

        return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab_id]))

    else:

        pretty_params = []

        json_url_params = expt_info.json_url_params()

        for key, val in json.loads(json_url_params).items():
            pretty_params.append(key + '=' + val)

        context = {
            'expt_info': expt_info,
            'pretty_params': '\n'.join(pretty_params),
        }

    template = 'experiment/experiment_params.html'
    return render(request, template, context)


def getbucket(data_bucket=False):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    extra = '-data' if data_bucket else ''

    return s3.Bucket(settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + extra)


@login_required
def command(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    action = request.POST.get('what')

    if action == "getfile":
        is_data_bucket = request.POST.get('type', 'experiment') == 'data'
        bucket = getbucket(data_bucket=is_data_bucket)
        filenam = request.POST.get('file')
        txt = None
        for key in bucket.objects.filter(Prefix=filenam):
            txt = key.get()['Body'].read()

        return HttpResponse(txt, content_type="text/plain", status=200)

    elif action == "savefile":
        try:
            is_data_bucket = request.POST.get('type', 'experiment') == 'data'
            bucket = getbucket(data_bucket=is_data_bucket)
            filenam = request.POST.get('filename')
            text = request.POST.get('text')

            for key in bucket.objects.filter(Prefix=filenam):
                key.put(Body=text, ContentType='text/html', ACL='public-read')
            else:
                bucket.put_object(Key=filenam, Body=text, ContentType='text/html')

            return HttpResponse(dumps({'status': 'success'}), content_type="application/json")
        except Exception as e:
            print("failed savefile", e)
            return json_result(request, {'status': 'fail'})

    elif action == "delete":
        is_data_bucket = request.POST.get('type', 'experiment') == 'data'
        bucket = getbucket(data_bucket=is_data_bucket)
        files = request.POST.getlist('files[]')
        keys = []
        for filename in files:
            k = {'Key': filename}
            keys.append(k)

        try:
            bucket.delete_objects(Delete={'Objects': keys})
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('delete error', e)
            return json_result(request, {'status': 'failure', 'xptFile': 'true'})
    elif action == "delete_all":
        try:
            delete_s3_dir(expt_info)
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('ERROR delete_all: ' + e)
            return json_result(request, {'status': 'failure', 'xptFile': 'true'})
    elif action == "s3_mb":

        try:
            is_data_bucket = request.POST.get('type', 'experiment') == 'data'
            bucket = getbucket(data_bucket=is_data_bucket)

            keys = bucket.objects.filter(Prefix=expt_id + '/')
            _dir = []
            size = 0

            for key in keys:
                size += key.size
                _dir.append(key.key)

            data = {
                "size": size,
                "max": settings.AWS_MAX_SIZE_MB,
                "dir": _dir,
                'status': 'success',
            }
            return HttpResponse(dumps(data), content_type="application/json")

        except Exception as e:
            create_bucket_url = reverse('create_bucket')
            message = f'you may need to set up your aws s3 bucket (it should be called "' \
                      f'{ settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME }). <a href="{ create_bucket_url }">Create it?</a>"'

            messages.error(request, mark_safe(message))
            return JsonResponse({}, status=400)

    elif action == "experimentDir":
        try:
            is_data_bucket = request.POST.get('type', 'experiment') == 'data'
            bucket = getbucket(data_bucket=is_data_bucket)
            bucket.put_object(Body='', Key=expt_info.expt_id + '/experiments/')
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('ERROR experimentDir: ', e)
            return json_result(request, {'status': 'failure', 'xptFile': 'true'})
    elif action == "new_dir":
        try:
            is_data_bucket = request.POST.get('type', 'experiment') == 'data'
            bucket = getbucket(data_bucket=is_data_bucket)
            bucket.put_object(Body='', Key=request.POST.get('new_dir'))
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('ERROR new_dir: ', e)

            return json_result(request, {'status': 'failure', 'xptFile': 'true'})

    elif action == "repos":
        # repos = request.POST.getlist('repos[]')
        # download_zip_upload_s3(repos, getbucket(), expt_info.expt_id)
        # expt_info
        pass

    return json_result(request, {'status': 'fail'})


def delete_s3_dir(expt_info):
    try:
        bucket = getbucket()
        keys = bucket.objects.filter(Prefix=expt_info.expt_id + '/')
        key_list = []
        for key in keys:
            key_list.append(key.key)
        if len(key_list) > 0:
            bucket.delete_objects(Delete={'Objects': key_list})
    except Exception as e:
        print('ERROR: ' + e)


@login_required
def create_bucket(request):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    try:
        s3.create_bucket(Bucket=settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME,
                         CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
    except Exception as e:
        messages.error(request, mark_safe(
            '<b>there was an error when attempting to create your experiment bucket:</b> ' + str(e)))
        return redirect(request.META.get('HTTP_REFERER'))

    cors_configuration = {
        'CORSRules': [{
            'AllowedMethods': ['GET', 'POST', 'PUT'],
            'AllowedOrigins': ['*'],
            'AllowedHeaders': ['*'],
        }]
    }

    bucket_configuration = json.dumps({
        "Version": "2008-10-17",
        "Statement": [
            {
                "Sid": "AllowPublicRead",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::" + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + "/*"
            }
        ]
    })

    bucket = getbucket()

    cors = bucket.Cors()
    cors.put(CORSConfiguration=cors_configuration)

    bucket_policy = bucket.Policy()
    bucket_policy.put(Policy=bucket_configuration)

    # we also need to create a separate bucket for data. This bucket needs to be private and not internet accessible.
    cors_configuration = {
        'CORSRules': [{
            'AllowedMethods': ['GET'],
            'AllowedOrigins': ['*'],
            'AllowedHeaders': ['Authorization'],
        }]
    }
    try:
        s3.create_bucket(Bucket=settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '-data',
                         CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
    except Exception as e:
        messages.error(request, mark_safe(
            '<b>there was an error when attempting to create your data bucket (your experiment bucket was successfully '
            'created however):</b> ' + str(
                e)))
        return redirect(request.META.get('HTTP_REFERER'))

    bucket = getbucket(data_bucket=True)
    cors = bucket.Cors()
    cors.put(CORSConfiguration=cors_configuration)

    cors = bucket.Cors()

    messages.success(request, 'successfully created your experiment and data buckets')
    return redirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def data(request, expt_id=None, uuid=None):
    if expt_id is None:
        return JsonResponse({'error': 'expt_id not specified'}, status=400)
    if uuid is None:
        return JsonResponse({'error': 'participant uuid not specified'}, status=400)

    text = request.POST.get('data', None)
    if text is None:
        return JsonResponse({'error': 'not given "data" parameter holding your data to save'}, status=400)

    if len(text) == 0:
        return JsonResponse({'error': '"data" parameter holds no data!'}, status=400)

    try:
        filenam = expt_id + '/' + uuid + '.txt'
        bucket = getbucket(data_bucket=True)
        bucket.put_object(Key=filenam, Body=text)
        return JsonResponse({'success': True, 'expt_id': expt_id, 'uuid': uuid}, status=201)

    except Exception as e:
        print(e, 22)
        return JsonResponse({'error': 'unknown'}, status=403)
