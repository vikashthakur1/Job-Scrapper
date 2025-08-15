# jobs/admin.py
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title","company","location","source","created_at")
    list_filter = ("source","location","created_at")
    search_fields = ("title","company","description","link")


