
from django.contrib import admin
from .models import *

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff', 'date_joined']
admin.site.register(User, UserAdmin)

class HistoryAdmin(admin.ModelAdmin):
    model = History
    list_display = ['id', 'created_at']
admin.site.register(History, HistoryAdmin)