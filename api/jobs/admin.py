
from django.contrib import admin
from .models import *

# Register your models here.
class JobAdmin(admin.ModelAdmin):
    model = Job
    list_display = ['employer', 'title', 'slug']
admin.site.register(Job, JobAdmin)

class JobTypeAdmin(admin.ModelAdmin):
    model = JobType
    list_display = ['name', 'slug']
admin.site.register(JobType, JobTypeAdmin)

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ['name', 'slug']
admin.site.register(Tag, TagAdmin)

class CountryAdmin(admin.ModelAdmin):
    model = Country
    list_display = ['name']
admin.site.register(Country, CountryAdmin)