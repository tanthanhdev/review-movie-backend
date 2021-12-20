
from django.contrib import admin
from .models import *
from api.reviews.models import *
# Register your models here.
class ReviewsInline(admin.TabularInline):
    model = Review
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    model = Product
    # filter_horizontal = ('country', 'genre', 'company', 'language', 'cast', 'crew') 
    list_display = ['id', 'title', 'slug']
    search_fields = ['title']
    inlines = (ReviewsInline, )
admin.site.register(Product, ProductAdmin)

class CountryAdmin(admin.ModelAdmin):
    model = Country
    list_display = ['english_name', 'iso_3166_1']
admin.site.register(Country, CountryAdmin)

class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display = ['name']
admin.site.register(Company, CompanyAdmin)

class LanguageAdmin(admin.ModelAdmin):
    model = Language
    list_display = ['name']
admin.site.register(Language, LanguageAdmin)

class GenreAdmin(admin.ModelAdmin):
    model = Genre
    list_display = ['id', 'name']
admin.site.register(Genre, GenreAdmin)

class CastAdmin(admin.ModelAdmin):
    model = Cast
    list_display = ['name']
admin.site.register(Cast, CastAdmin)

class CrewAdmin(admin.ModelAdmin):
    model = Crew
    list_display = ['name']
admin.site.register(Crew, CrewAdmin)

class VideoAdmin(admin.ModelAdmin):
    model = Video
    list_display = ['name']
admin.site.register(Video, VideoAdmin)