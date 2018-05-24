from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import ExptInfo, ExptAnswer, QuestionOrder


class ExptInfoAdmin(ModelAdmin):
    """Admin panel class for Post"""
    date_hierarchy = 'created'
    list_display = ('expt_id', 'name', 'creator', 'created')
    search_fields = ('expt_id', 'name', 'creator')
    prepopulated_fields = {'slug': ('name',)}

    # http://stackoverflow.com/questions/753704/manipulating-data-in-djangos-admin-panel-on-save
    def save_model(self, request, obj, form, change):
        """Customize save method via admin panel save"""
        if not change:
            obj.creator = request.user
        obj.save()


class ExptAnswerAdmin(ModelAdmin):
    """Admin panel class for Post"""
    date_hierarchy = 'created'
    list_display = ('id', 'uuid', 'expt_id', 'between_sjs_id', 'time_start',
                    'time_zone', 'time_stored', 'client_ip', 'expt_data', 'created')


class ExptInfoAttachmentAdmin(ModelAdmin):
    list_display = ('user', 'expt_info', 'name', 'file')


class QuestionOrderAdmin(ModelAdmin):
    list_display = ('expt_info', 'order', 'number')


admin.site.register(ExptInfo, ExptInfoAdmin)
admin.site.register(ExptAnswer, ExptAnswerAdmin)
admin.site.register(QuestionOrder, QuestionOrderAdmin)

