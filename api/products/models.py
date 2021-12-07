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
CURRENCY_CHOICES =(
  ("VND", "vnd"),
  ("USD", "dollar"),
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
    name = models.CharField(max_length=255, null=True, blank=True)
    iso_3166_1 = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'countries'
        
    def __str__(self):
        return self.name

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


# Table Product
class Product(models.Model):
    country = models.ManyToManyField(Country, db_table='products_countries', related_name='products_countries')
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
    overview = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
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
        db_table = 'jobs'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # slug save
        self.slug = unique_slugify(self, slugify(self.title))
        # ========================
        super(Job, self).save(*args, **kwargs)