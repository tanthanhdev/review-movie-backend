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
from api.employers.models import Employer

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
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'countries'
        
    def __str__(self):
        return self.name

# Table Tag
class Tag(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'tags'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
            # slug save
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.name))
        # ========================
        super(Tag, self).save(*args, **kwargs)

# Table Job type
class JobType(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'job_typies'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # slug save
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.name))
        # ========================
        super(JobType, self).save(*args, **kwargs)

# Table Job
class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, null=True, blank=True, related_name="jobs")
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    tag = models.ManyToManyField(Tag, db_table='jobs_tags', related_name='jobs_tags')
    #
    title = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_size = models.BigIntegerField(null=True, blank=True)
    # company_location = models.CharField(max_length=255, null=True, blank=True)
    company_location = models.CharField(max_length=100, null=True, blank=True, choices=LOCATION_CHOICES, default=LOCATION_CHOICES[0])
    hirer_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    salary = models.BigIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=100, null=True, blank=True, choices=CURRENCY_CHOICES, default=CURRENCY_CHOICES[0])
    web_link = models.CharField(max_length=255, null=True, blank=True)
    view_number = models.BigIntegerField(null=True, blank=True)
    package_type = models.CharField(max_length=255, null=True, blank=True, choices=PACKAGE_CHOICES, default=PACKAGE_CHOICES[0])
    is_active = models.BooleanField(default=False, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
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