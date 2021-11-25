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

from .manager import CustomUserManager
# Create your models here.

# iterable
GENDER_CHOICES =(
  ("Female", "female"),
  ("Male", "male"),
  ("Other", "other"),
)

def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

# extend User system table
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(('first name'), max_length=30)
    last_name = models.CharField(('last name'), max_length=150)
    email = models.EmailField(('email address'), unique=True)
    username = models.CharField(blank=True, max_length=30)
    is_staff = models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(default=True, help_text='Designates whether this user should be treated as active.\
                                              Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)
    #
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    forgot_password_token = models.TextField(null=True)
    expired = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    objects = CustomUserManager()
    
    class Meta:
        ordering = ('-pk',)
        db_table = 'users'

    def __str__(self):
        return self.email