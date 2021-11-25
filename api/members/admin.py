
from django.contrib import admin
from .models import *

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    model = Member
    list_display = ['user', 'member_user_email']
admin.site.register(Member, MemberAdmin)
