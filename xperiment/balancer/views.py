import json
from random import random, shuffle
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import Http404
from django.shortcuts import render
from balancer.models import BalanceItem
from core.utils import json_result
from django.core import serializers


@login_required
def change_orderings(request, group_id, template='balancer/change_order.html', extra_context=None):
    context = construct_table_info(group_id)
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def construct_table_info(group_id):
    order_list = serializers.serialize('json', BalanceItem.objects.filter(group_id=group_id).order_by('-created'),
                                       fields=('ordering', 'count'))
    return {'order_list': order_list}


@login_required
def delete_order(request, group_id):
    order_ids = request.POST.getlist('order_ids[]', None)

    if order_ids and len(order_ids) > 0:
        try:
            BalanceItem.objects.filter(pk__in=order_ids, group_id=group_id).delete()
            result = {
                'status': 'success',
                'objects': []
            }
            result.update(construct_table_info(group_id))
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
def order_batch_modify_order(request, group_id):
    result = None

    try:
        rows = json.loads(request.POST.get('modify_order'))
        print(rows)

        for row in rows:
            bi = BalanceItem.objects.get(pk=row[u'pk'])
            if bi is not None:
                bi.count = int(row[u'count'])
                bi.save()
        result = {
            'status': 'success',
            'objects': []
        }
        result.update(construct_table_info(group_id))

    except Exception as e:
        result = {
            'status': 'error',
            'message': e
        }

    return json_result(request, result)


@login_required
def reset_order_count(request, group_id):
    try:
        BalanceItem.objects.filter(group_id=group_id).update(count=0)
        result = {
            'status': 'success',
        }
        result.update(construct_table_info(group_id))
    except Exception as e:
            result = {
                'status': 'error',
                'message': e
            }

    return json_result(request, result)


@login_required
def order_batch_add(request, group_id):
    batch_order = request.POST.get('batch_order', None)
    ordering = None
    if batch_order:
        result = {
            'status': 'success',
            'items': []
        }

        json_orders = json.loads(batch_order)
        url_checker = URLValidator()

        for url in json_orders:
            try:
                url_checker(url)
            except ValidationError as e:
                result = {
                    'status': 'problem with a url',
                    'message': 'problem with this url: ' + url
                }

                return json_result(request, result)

        # for url in json_orders:
        #     try:
        #         resolve(url)
        #     except Http404 as e:
        #         print(e)
        #         result = {
        #             'status': 'problem with a url',
        #             'message': 'this url does not point to a study in this site: ' + url
        #         }
        #         return json_result(request, result)

        try:
            for ordering in json_orders:
                    if len(ordering) > 0:
                        balance_item, created = BalanceItem.objects.get_or_create(group_id=group_id, ordering=ordering)
                        if created:
                            balance_item.save()

            result.update(construct_table_info(group_id))


        except Exception as e:
            result = {
                'status': 'error',
                'message': 'please let admin know'
            }
    else:
        result = {
            'status': 'error',
            'message': 'batch order items can not be empty'
        }

    return json_result(request, result)


def rand_from_balancer(group_id, variation=.2):

    found = BalanceItem.objects.filter(group_id=group_id)
    if found is None:
        return None

    print(found,2323)
    counts = []
    total = 0.0
    for item in found:
        counts.append({
            'count': item.count,
            'item': item,
            'ordering': item.ordering
        })
        total += item.count

    if len(counts) == 0:
        return None

    least = 100
    least_item = None

    if len(counts) == 1:
        least_item = counts[0]['item']

    elif total == 0:
        least_item = shuffle(counts)[0]['item']

    else:
        for item in counts:
            val = float(item['count']) / total
            val += random() * variation #add some variation
            if least > val:
                least = val
                least_item = item['item']

    least_item.count += 1
    least_item.save()

    return least_item.ordering
