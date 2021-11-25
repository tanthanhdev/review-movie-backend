
from django.contrib import admin
from .models import *

# Register your models here.
class EmployerAdmin(admin.ModelAdmin):
    model = Employer
    list_display = ['user', 'employer_user_email']
admin.site.register(Employer, EmployerAdmin)

class CompanyFileAdmin(admin.ModelAdmin):
    model = CompanyFile
    list_display = ['employer', 'image']
admin.site.register(CompanyFile, CompanyFileAdmin)