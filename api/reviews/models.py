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
from api.products.models import Product

# Create your models here.
STATUS_CHOICES =(
  ("Disable", "disable"),
  ("Active", "active"),
)
# Table Reviews
class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews_users', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, related_name='reviews_products', on_delete=models.CASCADE, null=True, blank=True)
    #
    author = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    rating = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0])
    url = models.CharField(max_length=255, null=True, blank=True)
    id_temp = models.CharField(max_length=255, null=True, blank=True)
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ('-pk',)
        db_table = 'reviews'
    
    def __str__(self):
        return self.content