from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from s3direct.fields import S3DirectField
from django.db import transaction
import uuid
from django.utils.text import slugify 
from django.utils.crypto import get_random_string
from django.core.validators import validate_image_file_extension
from django.db.models.signals import post_save
from django.dispatch import receiver
# Models
from api.users.models import User

# Create your models here.
STATUS_CHOICES =(
  ("In Production", "In Production"),
  ("Released", "Released"),
)

PACKAGE_CHOICES =(
  ("Free", "free"),
  ("Basic", "basic"),
  ("Advance", "advance"),
)

LOCATION_CHOICES =(
  ("Tất Cả Địa Điểm", "tat ca dia diem"),
  ("Đà Nẵng", "da nang"),
  ("Hà Nội", "ha noi"),
  ("Tp. Hồ Chí Minh", "ho chi minh"),
  ("Quảng Nam", "quang nam"),
)

def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

# Table Country
class Country(models.Model):
    english_name = models.CharField(max_length=255, null=True, blank=True)
    native_name = models.CharField(max_length=255, null=True, blank=True)
    iso_3166_1 = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'countries'
        
    def __str__(self):
        return self.english_name

# # Table Tag
# class Tag(models.Model):
#     name = models.CharField(max_length=255, null=True, blank=True)
#     slug = models.CharField(max_length=255, null=True, blank=True)
#     #
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

#     class Meta:
#         ordering = ('-pk',)
#         db_table = 'tags'
    
#     def __str__(self):
#         return self.name
    
#     def save(self, *args, **kwargs):
#             # slug save
#         if not self.slug:
#             self.slug = unique_slugify(self, slugify(self.name))
#         # ========================
#         super(Tag, self).save(*args, **kwargs)


# Table Genres
class Genre(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'genres'
    
    def __str__(self):
        return self.name

        
#Table companies
class Company(models.Model):
    country = models.ManyToManyField(Country, db_table='companies_countries', related_name='companies_countries')
    #
    name = models.CharField(max_length=255, null=True, blank=True)
    logo_path = models.CharField(max_length=255, null=True, blank=True)
    origin_country = models.CharField(max_length=20, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'companies'
        verbose_name = 'companie' #change name on admin side
    
    def __str__(self):
        return self.name

    
#Table languages
class Language(models.Model):
    country = models.ManyToManyField(Country, db_table='languages_countries', related_name='languages_countries')
    #
    iso_639_1 = models.CharField(max_length=255, null=True, blank=True)
    english_name = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'languages'
        verbose_name = 'language' #change name on admin side
    
    def __str__(self):
        return self.name


# Table Casts
class Cast(models.Model):
    adult = models.CharField(max_length=255, null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True)
    known_for_department = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    original_name = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    profile_path = models.CharField(max_length=255, null=True, blank=True)
    cast_id = models.IntegerField(null=True, blank=True)
    character = models.CharField(max_length=255, null=True, blank=True)
    credit_id = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('pk',)
        db_table = 'casts'
    
    def __str__(self):
        return self.name
    
# Table Crews
class Crew(models.Model):
    adult = models.CharField(max_length=255, null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True)
    known_for_department = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    original_name = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.IntegerField(null=True, blank=True)
    profile_path = models.CharField(max_length=255, null=True, blank=True)
    cast_id = models.IntegerField(null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    job = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'crews'
    
    def __str__(self):
        return self.name


# Table Product
class Product(models.Model):
    country = models.ManyToManyField(Country, db_table='products_countries', related_name='products_countries')
    genre = models.ManyToManyField(Genre, db_table='products_genres', related_name='products_genres')
    company = models.ManyToManyField(Company, db_table='products_companies', related_name='products_companies')
    language = models.ManyToManyField(Language, db_table='products_languges', related_name='products_languges')
    cast = models.ManyToManyField(Cast, db_table='products_casts', related_name='products_casts')
    crew = models.ManyToManyField(Crew, db_table='products_crews', related_name='products_crews')
    #
    slug = models.CharField(max_length=255, null=True, blank=True)
    adult = models.BooleanField(default=False, null=True, blank=True)
    backdrop_path = models.CharField(max_length=255, null=True, blank=True)
    belongs_to_collection = models.CharField(max_length=255, null=True, blank=True)
    budget = models.BigIntegerField(null=True, blank=True)
    homepage = models.CharField(max_length=255, null=True, blank=True)
    imdb_id = models.CharField(max_length=255, null=True, blank=True)
    original_language = models.CharField(max_length=255, null=True, blank=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True, choices=STATUS_CHOICES)
    tagline = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    video = models.BooleanField(null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'products'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # slug save
        self.slug = unique_slugify(self, slugify(self.title))
        # ========================
        super(Product, self).save(*args, **kwargs)

TYPE_CHOICES =(
  ("Trailer", "Trailer"),
  ("Teaser", "Teaser"),
)

# Table Video
class Video(models.Model):
    product = models.ForeignKey(Product, related_name='videos_products', on_delete=models.CASCADE)
    #
    iso_639_1 = models.CharField(max_length=20, null=True, blank=True)
    iso_3166_1 = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, null=True, blank=True)
    site = models.CharField(max_length=255, null=True, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, null=True, blank=True)
    official = models.BooleanField(default=False, blank=True)
    published_at = models.CharField(max_length=255, null=True, blank=True)
    id_temp = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'videos'
    
    def __str__(self):
        return self.name