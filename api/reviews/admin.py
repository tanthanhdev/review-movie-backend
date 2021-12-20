
from django.contrib import admin
from .models import *

# Register your models here.
class ReviewAdmin(admin.ModelAdmin):
    model = Review
    list_display = ['content', 'status']
admin.site.register(Review, ReviewAdmin)
