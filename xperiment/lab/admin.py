from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from .models import Lab, LabScientist


class LabScientistInline(TabularInline):
    model = LabScientist


class LabAdmin(ModelAdmin):
    """Admin panel class for Post"""
    date_hierarchy = 'created'
    list_display = ('name', 'creator', 'website', 'email', 'phone', 'created')
    search_fields = ('name', 'creator')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [LabScientistInline,]

    #http://stackoverflow.com/questions/753704/manipulating-data-in-djangos-admin-panel-on-save
    def save_model(self, request, obj, form, change):
        """Customize save method via admin panel save"""
        if not change:
            obj.creator = request.user
        obj.save()


admin.site.register(Lab, LabAdmin)
