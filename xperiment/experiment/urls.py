from django.conf.urls import url
from experiment import views

urlpatterns = [

    url(r'^(?P<lab_id>\d+)/experiment/manage/$', views.experiment_manage, name='experiment_manage'),
    url(r'^(?P<lab_id>\d+)/experiment/manage/archived', views.experiment_manage_archived,
        name='experiment_manage_archived'),
    url(r'^(?P<lab_id>\d+)/experiment/manage/command/$', views.experiment_manage_command,
        name='experiment_manage_command'),
    url(r'^experiment/(?P<expt_id>\w+)/edit/$', views.experiment_edit, name='experiment_edit'),
    url(r'^experiment/(?P<expt_id>\w+)/experiment_rename/$', views.experiment_rename, name='experiment_rename'),
    url(r'^experiment/(?P<expt_id>\w+)/experiment_params/$', views.experiment_params, name='experiment_urlparams'),
    url(r'^experiment/(?P<expt_id>\w+)/download_zip/$', views.download_zip, name='download_zip'),
    url(r'^experiment/(?P<expt_id>\w+)/edit/modal/$', views.experiment_edit,
       name='experiment_edit_modal', kwargs={'template': 'experiment/experiment_edit_modal.html',
                                             'extra_context': {'is_modal': True}}),
    url(r'^experiment/(?P<expt_id>\w+)/delete/answers/$', views.experiment_delete_answers, name='experiment_delete_answers'),
    url(r'^experiment/delete/answers/overview/$', views.experiment_delete_answers_overview,
        name='experiment_delete_answers_overview'),
    url(r'^experiment/(?P<expt_id>\w+)/(?P<slug>[\w-]+)/detail/$', views.experiment_detail,
       name='experiment_detail'),
    url(r'^experiment/(?P<expt_id>\w+)/run/$', views.experiment_run,
       name='experiment_run'),
    url(r'^experiment/delete/$', views.experiment_delete, name='experiment_delete'),
    url(r'^experiment/(?P<expt_id>\w+)/payment/$', views.experiment_payment, name='experiment_payment'),
    url(r'^experiment/(?P<expt_id>\w+)/payment/complete/$', views.experiment_payment_complete,
       name='experiment_payment_complete'),
    url(r'^experiment/(?P<expt_id>\w+)/refresh_cdn/$', views.refresh_cdn, name='refresh_cdn'),
    url(r'^experiment/(?P<expt_id>\w+)/results/$', views.experiment_answer, name='experiment_answer'),
    url(r'^experiment/(?P<expt_id>\w+)/resultsWholeFamily/$', views.experiment_answer_all_aliases, name='experiment_answer_alias_family'),
    url(r'^(?P<lab_id>\d+)/experiment/create_v2/$', views.experiment_create_v2, name='experiment_create_v2'),
    url(r'^experiment/(?P<expt_id>\w+)/create/question_/$', views.experiment_create_question_v2,
                               name='experiment_create_question_v2'),
    url(r'^experiment/edit/signS3/$', views.sign_s3,
       name='sign_s3'),
    url(r'^experiment/(?P<expt_id>\w+)/edit/command/$', views.command,
       name='command'),


    url(r'^experiment/(?P<expt_id>\w+)/run/(?P<filename>.+)/$', views.get_experiment_file,
       name='get_experiment_file'),

    url(r'^experiment/(?P<expt_id>\w+)/(?P<type>[-\w]+)/export/raw/$', views.export_answer_raw,
        name='export_answer_raw'),
    url(r'^experiment/(?P<expt_id>\w+)/(?P<type>[-\w]+)/export/answer_alternative/$', views.export_answer_alternative,
    name='export_answer_alternative'),
    url(r'^experiment/(?P<expt_id>\w+)/(?P<type>[-\w]+)/export/answer/$', views.export_answer,
       name='export_answer'),

    url(r'^stats/(?P<expt_id>\w+)/$', views.stats,
        name='experiment_stats'),
    url(r'^e/(?P<slug>[\w-]+)$', views.experiment_run_short_url, name='experiment_run_short_url'),

    url(r'^propertygrid/json/$', views.propertygrid_json, name='propertygrid_json'),


    url(r'^experiment/(?P<expt_id>\w+)/backup_upload/$', views.backup_upload,
        name='backup_upload'),
    url(r'^experiment/admin/answer/upload/$', views.admin_upload_experiment_answer,
       name='admin_upload_experiment_answer'),

    url(r'^experiment/(?P<expt_id>\w+)/change/order/$', views.experiment_change_order, name='experiment_change_order'),
    url(r'^experiment/(?P<expt_id>\w+)/order/delete/$', views.experiment_order_delete, name='experiment_order_delete'),
    url(r'^experiment/(?P<expt_id>\w+)/order/batch/add/$', views.experiment_order_batch_add, name='experiment_order_batch_add'),
    url(r'^experiment/(?P<expt_id>\w+)/order/batch/modify_order/$', views.experiment_order_batch_modify_order, name='experiment_order_batch_modify_order'),

    url(r'^experiment/add-data/$', views.add_data, name='add_data'),
    url(r'^experiment/backup_upload/$', views.backup_upload,
        name='backup_upload'),
    url(r'^experiment/admin/answer/upload/$', views.admin_upload_experiment_answer,
       name='admin_upload_experiment_answer'),
]

