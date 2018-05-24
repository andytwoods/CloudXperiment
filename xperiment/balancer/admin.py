from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from .models import BalanceItem


class BalanceItemAdmin(ModelAdmin):
    list_display = ('group_id', 'ordering', 'count')


admin.site.register(BalanceItem, BalanceItemAdmin)
