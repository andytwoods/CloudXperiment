from hashlib import sha1
import unicodecsv
import json
import boto3
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


from base64 import b64encode
from datetime import datetime, timedelta
from json import dumps
import hmac
import re

from django.template.defaultfilters import urlencode
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from core.utils import get_page, json_result, get_client_ip
from lab.models import PaymentRecord, LabScientist, Lab

from .models import ExptInfo, ExptAnswer, QuestionOrder

from .forms import RenameForm, ExptForm_v2


def experiment_list(request, template='experiment/experiment_list.html', extra_context=None):
    if request.user.is_authenticated():
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


def payment_process(expt_info):
    result = False
    if not expt_info.is_paid:
        balance = expt_info.lab.balance
        amount = expt_info.participant_count * 1.21

        if balance - amount >= 0:
            expt_info.lab.balance = balance - amount
            expt_info.lab.save()
            expt_info.is_paid = True
            expt_info.save()
            result = True
            PaymentRecord(lab=expt_info.lab, scientist=expt_info.creator, amount=-amount).save()
    else:
        result = True
    return result

@login_required
def experiment_edit(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if expt_info.alias:
        expt_info = expt_info.alias
    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404
    return experiment_create_question_v2(request, expt_info, expt_id)


@login_required
def experiment_delete_answers(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404

    ExptAnswer.objects.filter(expt_id=expt_id).all().delete()
    expt_info.expt_headers = '{}'
    expt_info.save()

    return HttpResponseRedirect(reverse_lazy('experiment_answer', args=[expt_info.expt_id]))


def experiment_delete_answers_overview(request):
    expt_id = request.POST['expt_id']
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)

    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404

    expt_info.exptanswer_set.all().delete()
    expt_info.expt_headers = '{}'
    expt_info.save()

    return JsonResponse({'success': True}, status=200)



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

    if request.user.is_authenticated():
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


def stats(request, expt_id):

    found = ExptAnswer.objects.filter(expt_id=expt_id, expt_data__has_key='info_duration').values('expt_data')

    stats = {'expt_id': expt_id, 'count': found.count()}

    sex = {'male': 0, 'female': 0}

    for sj in found:
        data = sj.get('expt_data')
        my_sex = str(data.get('demographics_sex'))
        if my_sex in sex:
            sex[my_sex] += 1
        else:
            sex[my_sex] = 1

    stats['sex'] = sex


    return HttpResponse(json.dumps(stats, sort_keys=True, indent=4), content_type="application/json")


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
        print(e,33)
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


@login_required
def experiment_payment(request, expt_id, template='experiment/experiment_payment.html', extra_context=None):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404

    # TODO: Add paypal form

    context = {
        'expt_info': expt_info,
        'amount': expt_info.participant_count * 1.21,
        'payment_amount': expt_info.participant_count * 1.21 - expt_info.lab.balance
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


@login_required
def experiment_payment_complete(request, expt_id):
    try:
        amount = float(request.POST.get('amount'))
        expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
        if not expt_info.lab.scientist_belong_this(request.user):
            raise Http404

        expt_info.lab.balance += amount
        PaymentRecord(lab=expt_info.lab, scientist=expt_info.creator, amount=amount).save()

        result = payment_process(expt_info)
        if result:
            return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab.id]))
        else:
            return HttpResponseRedirect(reverse_lazy('experiment_payment', args=[expt_info.expt_id]))
    except Exception as e:
        error(request, e.message)
        return HttpResponseRedirect(reverse_lazy('experiment_payment', args=[expt_id]))

@login_required
def experiment_create_question(request, expt_id, template='experiment/experiment_create_question.html',
                               extra_context=None):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404

    return experiment_create_question_v2(request, expt_info, expt_id)


@login_required
def export_answer_alternative(request, expt_id, type='csv'):
    return _export_data_to_csv(request, expt_id, 'old style')


@login_required
def export_answer_raw(request, expt_id, type='raw'):
    return _export_data_to_csv(request, expt_id, 'raw')


@login_required
def export_answer(request, expt_id, type='csv'):
    try:
        _min = request.GET['min']
        _max = request.GET['max']
    except KeyError:
        _min = None
        _max = None
    return _export_data_to_csv(request, expt_id, _min=_min, _max=_max)


def _export_data_to_csv(request, expt_id, style='', _min=None, _max=None):

    expt_info = ExptInfo.objects.get(expt_id=expt_id, is_delete=False)

    family_wise = request.META.get('HTTP_REFERER', '')
    headers = None

    if 'Family' in family_wise:
        expt_answers, headers = compile_kinder_answers(expt_id, expt_info)
        expt_info = expt_info.alias

    else:
        expt_answers = ExptAnswer.objects.filter(expt_id=expt_info.expt_id).order_by('id')

    try:

        if _min and _max:
            #  https://docs.djangoproject.com/en/1.11/topics/db/queries/#limiting-querysets
            expt_answers = expt_answers[_min:_max]

        response = HttpResponse(content_type='text/csv')

        if _min and _max:
            response['Content-Disposition'] = 'attachment; filename=xperiment_min' + str(_min) + '_max' + str(
                _max) + '.csv'
        else:
            response['Content-Disposition'] = 'attachment; filename=xperiment_%s.csv' % datetime.strftime(
                datetime.now(), '%Y%m%d%H%M%S%f')

        #  BOM  https://stackoverflow.com/questions/30288666/return-a-csv-encoded-in-utf-8-with-bom-from-django

        exclude_unfinished = request.GET.get('exclude_unfinished', 'false') == 'true'

        if style == 'old style':
            response.write("\xEF\xBB\xBF")
            writer = unicodecsv.writer(response, encoding='utf', dialect='excel')
            write_csv_old_style(writer, expt_info, expt_answers, trial_data=headers)
        elif style == 'raw':
            writer = unicodecsv.writer(response, encoding='utf', lineterminator='\r\n', quotechar=" ")
            write_raw(writer, expt_info, expt_answers, trial_data=headers)
        elif style == 'zip':
            # nb same as below 'new style'
            response.write("\xEF\xBB\xBF")
            writer = unicodecsv.writer(response, encoding='utf', dialect='excel')
            write_csv(writer, expt_info, expt_answers, trial_data=headers, exclude_unfinished=exclude_unfinished)
        else:
            response.write("\xEF\xBB\xBF")
            writer = unicodecsv.writer(response, encoding='utf', dialect='excel')
            write_csv(writer, expt_info, expt_answers, trial_data=headers, exclude_unfinished=exclude_unfinished)

        return response

    except ExptInfo.DoesNotExist:
        raise Http404


@login_required
def refresh_cdn(request, expt_id):
    raise('sort out')
    c = boto3.connect_cloudfront(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

    inval = c.create_invalidation_request(settings.CDN_ID, ['/'+expt_id+'*'])

    return json_result(request, {'inval_id': inval.id, 'status': inval.status})


@login_required
def experiment_answer_all_aliases(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    expt_answers, headers = compile_kinder_answers(expt_id, expt_info)

    messages.info(request, 'combined family-wise results for all aliases of ' + expt_info.alias.name)
    return experiment_answer(request, expt_info.expt_id, expt_answers=expt_answers)




def compile_kinder_answers(expt_id, expt_info):
    if expt_info.alias is None:
        raise AttributeError('should never have non alias experiments here:' + expt_id)
    kinder_IDs = list(ExptInfo.objects.filter(alias=expt_info.alias).values_list('expt_id', flat=True))

    unique_headers = set()
    headers = expt_info.alias.expt_headers.get('headers', [])
    unique_headers.update(headers)

    for kinder in ExptInfo.objects.filter(alias=expt_info.alias):
        headers = kinder.expt_headers.get('headers', [])
        unique_headers.update(headers)

    kinder_IDs.append(expt_info.alias.expt_id)
    expt_answers = ExptAnswer.objects.filter(expt_id__in=kinder_IDs).order_by('id')

    return expt_answers, {'headers': list(unique_headers)}


@login_required
def experiment_answer(request, expt_id, expt_answers=None, template='experiment/experiment_answer.html',
                      extra_context=None):

    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)

    if not expt_info.lab.scientist_belong_this(request.user):
        raise Http404

    if expt_answers is None:
        expt_answers = ExptAnswer.objects.filter(expt_id=expt_id).order_by('-created')

    paginator = get_page(request, expt_answers, 20)

    context = {
        'lab': expt_info.lab,
        'expt_info': expt_info,
        'paginator': paginator,
    }

    if extra_context:
        context.update(extra_context)

    return render(request, template, context)


def write_raw(writer, expt_info, expt_answers=None):
    start = 0
    gap = 1000
    end = gap

    while True:
        block_of_evaluated_answers = list(expt_answers[start: end])
        if len(block_of_evaluated_answers) == 0:
            break
        start = end
        end += gap

        for expt_answer in block_of_evaluated_answers:
            if isinstance(expt_answer.expt_data, dict):
                my_data = json.dumps(expt_answer.expt_data, ensure_ascii=False)
            else:
                my_data = expt_answer.expt_data

            writer.writerow([my_data])


def write_csv_old_style(writer, expt_info, expt_answers=None, expt_headers=None):

    writer.writerow(['expt_id', expt_info.expt_id])
    writer.writerow(['name', expt_info.name])
    writer.writerow(['created', expt_info.created])

    writer.writerow([])
    expt_answer_list = expt_answers if expt_answers else list(expt_info.exptanswer_set.all())
    answer_head = ['ip', 'participant', 'uuid', 'overSJs', 'time_start', 'time_zone', 'time_stored', 'device_uuid']

    if expt_headers is None and expt_info.expt_headers is None:
        expt_info.expt_headers = {'headers': []}
        expt_info.save()
    answer_head.extend(expt_info.expt_headers['headers'])

    h_b = [0] * len(answer_head)
    h_i = [0] * len(answer_head)

    h1 = [0] * len(answer_head)
    h2 = [0] * len(answer_head)
    h3 = [0] * len(answer_head)
    h4 = [0] * len(answer_head)
    h5 = [0] * len(answer_head)
    h6 = [0] * len(answer_head)
    blank = [''] * len(answer_head)

    for i in range(0, len(answer_head)):
        splithead = answer_head[i].split("_")
        splithead = [j for j in splithead if j != '']

        splithead_len = len(splithead)


        h1[i] = splithead[0]

        matchObj = re.match( r'b\d+i\d+', h1[i] , re.M|re.I)
        if matchObj:
            bi_arr = matchObj.group().split('i')
            h_b[i] = bi_arr[0][1:]
            h_i[i] = bi_arr[1]
        else:
             h_b[i] = ''
             h_i[i] = ''

        if splithead_len >= 2:
            h2[i] = splithead[1]
        else:
            h2[i] = ''
        if splithead_len >= 3:
            remain = splithead[2]
            h3[i] = remain
        else:
            h3[i] = ''
        if splithead_len >= 4:
            remain = splithead[3]
            h4[i] = remain
        else:
            h4[i] = ''
        if splithead_len >= 5:
            remain = splithead[4]
            h5[i] = remain
        else:
            h5[i] = ''
        if splithead_len >= 6:
            remain = splithead[5]
            for j in range(6, splithead_len):
                remain = remain + "_" + splithead[j]
            h6[i] = remain
        else:
            h6[i] = ''

    #answer_head[i] = answer_head[i].replace('_', ' ')
    writer.writerow(h_b)
    writer.writerow(h_i)
    writer.writerow(blank)
    writer.writerow(answer_head)
    writer.writerow(h1)
    writer.writerow(h2)
    writer.writerow(h3)
    writer.writerow(h4)
    writer.writerow(h5)
    writer.writerow(h6)
    writer.writerow(blank)
    for expt_answer in expt_answer_list:
        email = None
        if expt_answer.user:
            email = expt_answer.user.email
        answer_value = [expt_answer.client_ip, email, expt_answer.uuid,
                        expt_answer.between_sjs_id, expt_answer.time_start, expt_answer.time_zone,
                        expt_answer.time_stored, expt_answer.device_uuid]


        my_headers = expt_info.expt_headers['headers']


        if isinstance(expt_answer.expt_data, dict):
            my_data = expt_answer.expt_data
        else:
            my_data = json.loads(expt_answer.expt_data)

        for header in my_headers:
            answer_value.append(my_data.get(header, ''))

        writer.writerow(answer_value)



def write_csv(writer, expt_info, expt_answers=None, trial_data=None, exclude_unfinished=False):

    writer.writerow(['expt_id', expt_info.expt_id])
    writer.writerow(['name', expt_info.name])
    writer.writerow(['created', expt_info.created])

    writer.writerow([])

    answer_head = [' ', 'ip', 'uuid', 'overSJs', 'time_start',
                   'time_zone', 'time_stored', 'device_uuid']

    if trial_data is None:
        trial_data = expt_info.expt_headers
        if trial_data is None:
            trial_data = {'headers': []}
            expt_info.expt_headers = trial_data
            expt_info.save()

    trial_data['headers'].sort()
    answer_head = trial_data['headers'] + answer_head

    h_b = [0] * len(answer_head)
    h_i = [0] * len(answer_head)

    h1 = [0] * len(answer_head)
    h2 = [0] * len(answer_head)
    h3 = [0] * len(answer_head)
    blank = [''] * len(answer_head)

    for i in range(0, len(answer_head)):
        splithead = answer_head[i].split("_")
        splithead = [j for j in splithead if j != '']

        h1[i] = splithead[0]

        matchObj = re.match(r'b\d+i\d+', h1[i], re.M|re.I)
        if matchObj:
            bi_arr = matchObj.group().split('i')
            h_b[i] = bi_arr[0][1:]
            h_i[i] = bi_arr[1]
        else:
             h_b[i] = ''
             h_i[i] = ''

        if len(splithead) >= 2:
            h2[i] = splithead[1]
        else:
            h2[i] = ''
        if len(splithead) >= 3:
            remain = splithead[2]
            for j in range(3, len(splithead)):
                remain = remain + "_" + splithead[j]
            h3[i] = remain
        else:
            h3[i] = ''

    for i in range(0, len(h_b)):
        if h_b[i] == '':
            h_b[i] = ':block'
            break

    for i in range(0, len(h_i)):
        if h_i[i] == '':
            h_i[i] = ':iteration'
            break

    #answer_head[i] = answer_head[i].replace('_', ' ')

    writer.writerow(h_b)
    writer.writerow(h_i)
    writer.writerow(blank)
    writer.writerow(answer_head)
    writer.writerow(h1)
    writer.writerow(h2)
    writer.writerow(h3)
    writer.writerow(blank)

    start = 0
    gap = 1000
    end = gap

    while True:
        block_of_evaluated_answers = list(expt_answers[start: end])
        if len(block_of_evaluated_answers) == 0:
            break
        start = end
        end += gap

        for expt_answer in block_of_evaluated_answers:
            if exclude_unfinished is True:
                if expt_answer.time_stored is None:
                    continue

            answer_value = []

            if isinstance(expt_answer.expt_data, dict):
                my_data = expt_answer.expt_data
            else:
                my_data = json.loads(expt_answer.expt_data)

            for header in trial_data['headers']:
                answer_value.append(my_data.get(header, ''))


            answer_value += [' ', expt_answer.client_ip, expt_answer.uuid, expt_answer.between_sjs_id,
                             expt_answer.time_start, expt_answer.time_zone,
                             expt_answer.time_stored, expt_answer.device_uuid]

            writer.writerow(answer_value)


@login_required
def api_upload_xml(request):
    expt_id = request.POST.get('expt_id', None)
    xml = request.POST.get('xml', None)

    try:
        if expt_id:
            expt_info = ExptInfo.objects.get(expt_id=expt_id, is_delete=False)
            xml_file = ContentFile(xml)
            expt_info.xml.save('%s.xml' % expt_info.expt_id, xml_file)
            expt_info.is_publish = True
            expt_info.save()
            data = {'status': 'success'}
        else:
            data = {'status': 'success', 'message': 'parameter expt_id does not exists'}
    except Exception as e:
        data = {'status': 'error', 'message': e.message}
    return json_result(request, data)



@csrf_exempt
def propertygrid_json(request):
    data = request.POST.get('data', {})
    return json_result(request, json.loads(data))


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


def backup_upload(request, expt_id=None):

    backups = request.POST.get('backup')

    if len(backups) == 0:
        return JsonResponse({'status': 'no data given!'})

    fails = []

    err = "the backup data was not in String64 format, json, or prop:val tab-separated: "

    for backup in backups.split('\n'):
        my_json = None
        if len(backup) == 0:
            continue

        try:
            my_json = json.loads(backup)
        except Exception as e:
            pass

        if my_json is None:

            try:
                backup = backup.decode('base64')
                my_json = json.loads(backup)

            except Exception as e:
                my_json = tab_sep_to_dict(backup)

                if my_json is None:
                    fails.append(err + backup)
                    continue

        if expt_id is None:
            try:
                expt_id = my_json[specialTag + 'expt_id']
            except KeyError:
                fails.append('no expt_id:<------>' + backup)
                continue
            except:
                fails.append('possibly not json:<------>' + backup)
                continue

        try:
            expt_info = ExptInfo.objects.get(expt_id=expt_id)
        except ExptInfo.DoesNotExist:
            print('not exist')
            fails.append(backup)
            #fails.append('unknown expt_id:<------>' + backup)
            continue

        try:

            outcome = save_expt_answer(None, expt_info, my_json)

            if outcome != 'success':
                fails.append(backup)
                #fails.append('unknown a:<------>'+ backup)
        except KeyError:
            fails.append('unknown b:<------>' + backup)
        except Exception as e:

            fails.append(backup)
            #fails.append('unknown c:<------>' + backup)

    return JsonResponse({'success': 'success' if len(fails) == 0 else 'fail', 'fails': fails}, status=200)




@login_required
def admin_upload_experiment_answer(request, template='experiment/upload_experiment_answer.html', extra_context=None):
    context = {}

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)



@login_required
def get_finished_list(request, expt_id):

    finished_dict = {}
    finished_list = []

    try:
        expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)

        expt_answers = ExptAnswer.objects.filter(expt_info=expt_info, ).exclude(between_sjs_id=None)

        for expt_answer in expt_answers:
            between_sjs_id = expt_answer.between_sjs_id
            if hasattr(finished_dict, between_sjs_id):
                finished_dict[between_sjs_id] += 1
            else:
                finished_dict[between_sjs_id] = 1
        for key in finished_dict:
            finished_list.append({'finished': key, 'count': finished_dict.get(key)})

    except Exception as e:
            print('err',e)
    return finished_list

@login_required
def experiment_change_order(request, expt_id, template='experiment/change_order.html', extra_context=None):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    order_list = QuestionOrder.objects.filter(expt_info=expt_info)

    context = {
        'order_list': order_list,
        'finished_list': get_finished_list(request, expt_id),
    }

    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


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


#  __  __                _                      _      ____          _          __  __
#  \ \/ /_ __   ___ _ __(_)_ __ ___   ___ _ __ | |_   |___ \     ___| |_ _   _ / _|/ _|
#   \  /| '_ \ / _ \ '__| | '_ ` _ \ / _ \ '_ \| __|    __) |   / __| __| | | | |_| |_
#   /  \| |_) |  __/ |  | | | | | | |  __/ | | | |_    / __/    \__ \ |_| |_| |  _|  _|
#  /_/\_\ .__/ \___|_|  |_|_| |_| |_|\___|_| |_|\__|  |_____|   |___/\__|\__,_|_| |_|
#       |_|

def experiment2_run_expt(request, expt, extra_content=None):
    context = generate_context(request, expt, extra_content)
    return expt_run_v2(context, expt, request)


def expt_run_v2(initial_context, expt_info, request):

    initial_context['ip'] = urlencode(initial_context['client_ip'])
    initial_context['cloudUrl'] = urlencode(request.build_absolute_uri(reverse('sj_data')))
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
    url = settings.AWS_BUCKET_LOCATION+settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME+'/'+expt_id+'/'+filename
    return HttpResponseRedirect(url)


@login_required
def experiment_create_v2(request, lab_id, template='experiment/experiment_create_v2.html', extra_context=None):
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
def experiment_create_question_v2(request, expt_info, expt_id, template='experiment/experiment_create_question_v2.html',
                               extra_context=None):

    if request.method == 'POST':
        result = payment_process(expt_info)
        expt_info.is_publish = True
        expt_info.save()
        if result:
            return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab.id]))
        else:
            return HttpResponseRedirect(reverse_lazy('experiment_payment', args=[expt_info.expt_id]))

    context = {

        'expt_info': expt_info,
        'access_key': settings.AWS_ACCESS_KEY_ID,
        'bucket_url': settings.AWS_BUCKET_LOCATION+settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME+'/',
        'expt_id': expt_id,
        'xpt2_xml': expt_info.xpt2_xml,
        'github_projects': {'Xperiment2': 'https://github.com/andytwoods/Xperiment2/archive/master.zip', 'jsPsych+wrapper': 'https://github.com/andytwoods/jsPsychXptComms/archive/master.zip,https://github.com/jodeleeuw/jsPsych/archive/master.zip'}
    }

    if extra_context:
        context.update(extra_context)

    return render(request, template, context)


@login_required
def upload_experiment_attachment_v2(request, expt_info):
    u_file = request.FILES['file']
    content_type = u_file.content_type
    attachment_name = request.GET.get('attachment_name', u_file.name)

    return json_result(request, {'status':'success','xptFile':'true'})


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
def download_zip(request, expt_id, template='experiment/download_zip.html'):
    bucket = getbucket()
    keys = bucket.objects.filter(Prefix=expt_id + '/')
    files = []
    for key in keys:
        files.append(key.key)
    print(files)

    context = {'files': files,
               'dir':settings.AWS_BUCKET_LOCATION + settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME + '/'}

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
                print(key_val)
                if len(key_val) != 2:
                    errs.append('cannot add this key+value as not formatted correctly (x=y): ' + line)
                else:
                    params[key_val[0]] = key_val[1]

        expt_info.url_params = params
        expt_nam = expt_info.name

        if len(errs) > 0:
            messages.error(request, expt_nam + ': ' + '/n'.join(errs))

        messages.success(request, expt_nam +': added these url params: ' + dumps(params))

        expt_info.save()

        return HttpResponseRedirect(reverse_lazy('experiment_manage', args=[expt_info.lab_id]))

    else:

        pretty_params = []
        for key, val in expt_info.url_params.items():
            pretty_params.append(key+'='+val)

        context = {
            'expt_info': expt_info,
            'pretty_params': '\n'.join(pretty_params),
        }

    template = 'experiment/experiment_params.html'
    return render(request, template, context)


def getbucket():
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        return s3.Bucket(settings.AWS_STORAGE_EXPERIMENTS_BUCKET_NAME)

@login_required
def command(request, expt_id):
    expt_info = get_object_or_404(ExptInfo, expt_id=expt_id)
    action = request.POST.get('what')

    if action == "getfile":
        bucket = getbucket();
        filenam = request.POST.get('file')
        for key in bucket.objects.filter(Prefix=filenam):
            txt = key.get()['Body'].read()

        return HttpResponse(txt, content_type="text/plain", status=200)

    elif action == "savefile":
        try:
            bucket = getbucket()
            filenam = request.POST.get('filename')
            text = request.POST.get('text')
            for key in bucket.objects.filter(Prefix=filenam):
                key.put(Body=text, ContentType='text/html', ACL='public-read')

            return HttpResponse(dumps({'status':'success'}), content_type="application/json")
        except Exception as e:
            print("failed",e)
            return json_result(request, {'status':'fail'})

    elif action == "delete":
        bucket = getbucket()
        files = request.POST.getlist('files[]')
        keys = []
        for filename in files:
            k = {'Key': filename}
            keys.append(k)

        try:
            bucket.delete_objects(Delete={'Objects': keys})
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print(e)
    elif action == "delete_all":
        try:
            delete_s3_dir(expt_info)
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('ERROR: ' + e)
    elif action == "s3_mb":
        try:
            bucket = getbucket()
            keys = bucket.objects.filter(Prefix=expt_id+'/')
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
            print('ERROR: ' + e)

    elif action == "experimentDir":
        try:
            bucket = getbucket()
            bucket.put_object(Body='', Key=expt_info.expt_id+'/experiments/')
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('ERROR: ' + e)

    elif action == "new_dir":
        try:
            bucket = getbucket()
            bucket.put_object(Body='', Key=request.POST.get('new_dir'))
            return json_result(request, {'status': 'success', 'xptFile': 'true'})
        except Exception as e:
            print('ERROR: ' + e)

    elif action == "repos":
        #repos = request.POST.getlist('repos[]')
        #download_zip_upload_s3(repos, getbucket(), expt_info.expt_id)
        #expt_info
        pass



    return json_result(request, {'status':'fail'})

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


def add_data(request, template='experiment/add_data.html'):
    return render(request, template, {})
