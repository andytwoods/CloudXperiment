from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Profile


class ProfileAdmin(ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('user', 'title', 'fullname', 'website', 'phone', 'created')
    search_fields = ('name',)
    raw_id_fields = ('user',)


admin.site.register(Profile, ProfileAdmin)
