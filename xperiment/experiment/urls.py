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

    url(r'^experiment/delete/answers/overview/$', views.experiment_delete_answers_overview,
        name='experiment_delete_answers_overview'),
    url(r'^experiment/(?P<expt_id>\w+)/(?P<slug>[\w-]+)/detail/$', views.experiment_detail,
       name='experiment_detail'),
    url(r'^experiment/(?P<expt_id>\w+)/run/$', views.experiment_run,
       name='experiment_run'),
    url(r'^experiment/delete/$', views.experiment_delete, name='experiment_delete'),

    url(r'^(?P<lab_id>\d+)/experiment/create_v2/$', views.experiment_create_v2, name='experiment_create_v2'),
    url(r'^experiment/(?P<expt_id>\w+)/create/question_/$', views.experiment_create_question_v2,
                               name='experiment_create_question_v2'),
    url(r'^experiment/edit/signS3/$', views.sign_s3,
       name='sign_s3'),
    url(r'^experiment/(?P<expt_id>\w+)/edit/command/$', views.command,
       name='command'),


    url(r'^experiment/(?P<expt_id>\w+)/run/(?P<filename>.+)/$', views.get_experiment_file,
       name='get_experiment_file'),

    url(r'^e/(?P<slug>[\w-]+)$', views.experiment_run_short_url, name='experiment_run_short_url'),

    url(r'^experiment/(?P<expt_id>\w+)/order/delete/$', views.experiment_order_delete, name='experiment_order_delete'),
    url(r'^experiment/(?P<expt_id>\w+)/order/batch/add/$', views.experiment_order_batch_add, name='experiment_order_batch_add'),
    url(r'^experiment/(?P<expt_id>\w+)/order/batch/modify_order/$', views.experiment_order_batch_modify_order, name='experiment_order_batch_modify_order'),

    url(r'^experiment/create_bucket/$', views.create_bucket, name='create_bucket'),
]

