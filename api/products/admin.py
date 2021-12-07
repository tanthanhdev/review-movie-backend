
from django.contrib import admin
from .models import *

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ['title', 'slug']
admin.site.register(Product, ProductAdmin)

class CountryAdmin(admin.ModelAdmin):
    model = Country
    list_display = ['name']
admin.site.register(Country, CountryAdmin)