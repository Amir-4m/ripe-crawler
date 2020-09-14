from django.contrib import admin

from .models import RangeIP


@admin.register(RangeIP)
class RangeIPAdmin(admin.ModelAdmin):
    list_display = ['inet', 'created_time']
